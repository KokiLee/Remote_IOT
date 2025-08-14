# Iot Remote

## ラズパイ4の1-wireのデフォルトピンを変更する。

`boot/config/overlayREADME`に設定を方法が記載してあります。
5793行目

```md
Name: w1-gpio
Info: Configures the w1-gpio Onewire interface module.
      Use this overlay if you don't need a GPIO to drive an external pullup.
Load: dtoverlay=w1-gpio,<param>=<val>
Params: gpiopin     GPIO for I/O (default "4")
        pullup      Now enabled by default(ignored)
```

とあるので、boot/config/firmware/config.txtの51行目のコメントアウトを削除

```md
[all]
dtoverlay=w1-gpio,gpiopin=26
```

OneWireのPINを26番に変更する。

## ラズパイリモコンを外部から操作する

MyHomeのリモコンをMyWebSiteから送信されたデータで
On,Offするソフト。

## ラズパイリモコンに学習させる

エアコン、シーリングライトのリモコンをラズパイリモコンに
向けて照射し、学習させる。

## ラズパイリモコンをLearnMode

1. 基盤上のリップスイッチを操作してLearnModeにする。
   ※購入時はControlになっている。
2. 基盤上のLEDが青色になる。
3. 記憶させたいメモリを選択
   ※基板上のスイッチのどれかを押す。
