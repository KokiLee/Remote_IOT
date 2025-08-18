import io
import os
import select
import socket
import sys
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2
import numpy as np

HOST = "0.0.0.0"
PORT = 8080

# 配信パラメータ
CAP_WIDTH = 640
CAP_HEIGHT = 480
CAP_FPS = 24  # カメラ取得ターゲット
STREAM_FPS = 12  # 配信ターゲット（MJPEGは帯域重いので控えめ推奨）
JPEG_QUALITY = 60  # 画質と帯域のバランス
MAX_CLIENTS = 5  # 同時視聴制限（ルータ保護）
CLIENT_IDLE_TIMEOUT = 30  # クライアント側から受信が無いなどのアイドルで切断
WRITE_TIMEOUT = 5  # 送信スタックが詰まったときのタイムアウト

# 共有フレーム（JPEG化済み）を1つ持ち回し
latest_jpeg = None
latest_lock = threading.Lock()
stop_event = threading.Event()


def set_tcp_keepalive(sock: socket.socket):
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # Linux の場合（可能なら）
        if hasattr(socket, "TCP_KEEPIDLE"):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)
        if hasattr(socket, "TCP_KEEPINTVL"):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
        if hasattr(socket, "TCP_KEEPCNT"):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
    except Exception:
        pass


class FrameGrabber(threading.Thread):
    """カメラから一定FPSでフレームを取り、JPEG化して共有する"""

    def __init__(self, device=0):
        super().__init__(daemon=True)
        self.device = device
        self.cap = None

    def run(self):
        global latest_jpeg
        while not stop_event.is_set():
            try:
                if self.cap is None:
                    self.cap = cv2.VideoCapture(self.device)
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_WIDTH)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_HEIGHT)
                    self.cap.set(cv2.CAP_PROP_FPS, CAP_FPS)
                    # 可能ならMJPGで取り込む（遅延軽減）
                    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                    self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

                start = time.time()
                ret, frame = self.cap.read()
                if not ret or frame is None or frame.size == 0:
                    # 再初期化
                    self.cap.release()
                    self.cap = None
                    time.sleep(1.0)
                    continue

                # JPEGにエンコード
                ok, buf = cv2.imencode(
                    ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
                )
                if ok:
                    with latest_lock:
                        latest_jpeg = buf.tobytes()

                # 取り込みFPS調整
                elapsed = time.time() - start
                interval = 1.0 / CAP_FPS
                if elapsed < interval:
                    time.sleep(interval - elapsed)

            except Exception as e:
                # 予期せぬエラーでもループは継続
                print(f"[Grabber] Error: {e}", file=sys.stderr)
                time.sleep(1.0)
        # 終了処理
        try:
            if self.cap:
                self.cap.release()
        except:
            pass


active_clients = set()
clients_lock = threading.Lock()


class MJPEGHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print(
            f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {self.address_string()} - {fmt % args}"
        )

    def _send_html(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Connection", "close")
        self.end_headers()
        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>USBカメラストリーム</title>
<style>
body {{ font-family: system-ui, Arial; text-align:center; margin:20px; }}
img {{ border: 2px solid #333; border-radius: 8px; }}
</style></head>
<body>
  <h1>USBカメラ ライブストリーム (MJPEG)</h1>
  <div><img id="video" src="/stream" width="{CAP_WIDTH}" height="{CAP_HEIGHT}" /></div>
  <p>FPS: {STREAM_FPS} / JPEG品質: {JPEG_QUALITY} / 同時視聴上限: {MAX_CLIENTS}</p>
  <script>
  // 切断時に再接続（過剰リトライ抑制）
  let retry = 0;
  function reopen() {{
    if (retry > 10) return;
    retry++;
    document.getElementById('video').src = '/stream?t=' + Date.now();
  }}
  document.getElementById('video').onerror = () => setTimeout(reopen, 2000);
  </script>
</body></html>"""
        self.wfile.write(html.encode("utf-8"))

    def do_GET(self):
        if self.path == "/":
            self._send_html()
            return

        if self.path.startswith("/stream"):
            # クライアント制限
            with clients_lock:
                if len(active_clients) >= MAX_CLIENTS:
                    self.send_error(503, "Too many clients")
                    return
                active_clients.add(self.client_address)

            # 送信準備
            try:
                self.send_response(200)
                self.send_header(
                    "Content-Type", "multipart/x-mixed-replace; boundary=frame"
                )
                self.send_header(
                    "Cache-Control", "no-store, no-cache, must-revalidate, max-age=0"
                )
                self.send_header("Pragma", "no-cache")
                self.send_header("Connection", "close")
                self.end_headers()

                # ソケットオプション
                set_tcp_keepalive(self.connection)
                self.connection.settimeout(WRITE_TIMEOUT)

                frame_interval = 1.0 / STREAM_FPS
                next_ts = time.time()

                # 配信ループ
                last_activity = time.time()
                flush_every = 15  # 15フレームごとにflush
                n = 0

                while not stop_event.is_set():
                    # アイドル検知（読み取り方向にデータが来ない/エラー等で切断）
                    rlist, wlist, _ = select.select(
                        [self.connection], [self.connection], [], 0
                    )
                    now = time.time()
                    if rlist:
                        try:
                            # 相手から何か受信（HTTPでは通常来ないが、生存監視）
                            _ = self.connection.recv(1, socket.MSG_PEEK)
                            last_activity = now
                        except Exception:
                            # 切断とみなす
                            break
                    if now - last_activity > CLIENT_IDLE_TIMEOUT:
                        break

                    # 最新JPEGを取得
                    with latest_lock:
                        jpeg = latest_jpeg

                    if not jpeg:
                        time.sleep(0.01)
                        continue

                    # 送出時刻まで待つ
                    sleep_time = next_ts - time.time()
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    next_ts += frame_interval

                    # 書き込み可能かチェック
                    _, wlist, _ = select.select(
                        [], [self.connection], [], WRITE_TIMEOUT
                    )
                    if not wlist:
                        # 書き込みタイムアウト→切断
                        break

                    try:
                        # マルチパートチャンク送出（Content-Length 省略でOK）
                        self.wfile.write(b"--frame\r\n")
                        self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n")
                        self.wfile.write(jpeg)
                        self.wfile.write(b"\r\n")

                        n += 1
                        if n % flush_every == 0:
                            self.wfile.flush()
                    except (BrokenPipeError, ConnectionResetError, OSError):
                        break

                # 終了
            finally:
                with clients_lock:
                    active_clients.discard(self.client_address)
                try:
                    self.wfile.flush()
                except:
                    pass
                self.log_message("stream closed")

        else:
            self.send_error(404, "Not Found")


def check_camera(device=0):
    cap = cv2.VideoCapture(device)
    ok, frame = cap.read()
    cap.release()
    return ok and frame is not None and frame.size > 0


def main():
    if not check_camera(0):
        print("カメラが利用できません。終了します。", file=sys.stderr)
        sys.exit(1)

    grabber = FrameGrabber(device=0)
    grabber.start()

    srv = ThreadingHTTPServer((HOST, PORT), MJPEGHandler)
    print(f"HTTP(MJPEG) streaming: http://{HOST}:{PORT}")
    print(
        f"設定: CAP={CAP_WIDTH}x{CAP_HEIGHT}@{CAP_FPS} / STREAM_FPS={STREAM_FPS} / JPEG={JPEG_QUALITY}"
    )
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        try:
            srv.shutdown()
        except:
            pass


if __name__ == "__main__":
    main()
