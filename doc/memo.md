## DMR

rtsprelay.c
  - Service Unavailable (503)은 거의 클라이언트로 영상을 줄 수 없는 경우 발생하는듯 (영상을 받는 과정 자체가 안되거나 받아서 넘겨주는 과정에서 뭔가 문제가 있다는 뜻)

https://forums.developer.nvidia.com/t/problems-minimizing-latency-and-maximizing-quality-for-rtsp-and-mpeg-ts/67050/14

play하기 위해 연결하는 순간
기존 record하면서 호출되던 cb_buffer가 끊김

[multiudpsink example](https://stackoverflow.com/questions/41870834/gstreamer-emit-a-signal-to-an-element)

## Android

RTSP from VideoView:

VideoView doesn't seem to send OPTIONS Request to the server
or send DESCRIBE Request before the creation of a media factory at least.

Use pre-describe-request callback instead of options-request callback to create a media factory.
Return appropriate value in pre-describe-request callback.
[Reference](https://gstreamer.freedesktop.org/documentation/gst-rtsp-server/rtsp-client.html#GstRTSPClient::pre-describe-request)

### Server App (Termux)

#### install openssh
termux-change-repo > Main repository > Mirrors by Grimler
pkg upgrade
pkg install openssh

#### install debian

#### install packages
remove systemd
[remove systemd](https://askubuntu.com/questions/779640/how-to-remove-systemd-from-ubuntu-16-04-and-prevent-its-usage)
```sh
apt-get remove --purge --auto-remove systemd systemd:i386 -y
echo -e 'Package: systemd\nPin: release *\nPin-Priority: -1' > /etc/apt/preferences.d/systemd
echo -e '\n\nPackage: *systemd*\nPin: release *\nPin-Priority: -1' >> /etc/apt/preferences.d/systemd
echo -e '\nPackage: systemd:amd64\nPin: release *\nPin-Priority: -1' >> /etc/apt/preferences.d/systemd
echo -e '\nPackage: systemd:i386\nPin: release *\nPin-Priority: -1' >> /etc/apt/preferences.d/systemd
```

#### setup git bare repository
ln home debian home

set remote repository from local filesystem

git config receive.denynonfastforwards false


### Client App

[Gstreamer NDK Version](https://gstreamer.freedesktop.org/download/#android)
NDK Version `r21` for Gstreamer Version `1.20.x`

Windows에서 세팅하는경우
- cmd 에서 chocolatey 설치해서 `choco install pkgconfiglite` 로 pkg-config 설치

```
../sys/androidmedia/gst-android-hardware-camera.c:1763:_init_classes Failed to initialize android.hardware.Camera classes: Failed to get static field ID EFFECT_EMBOSS (Ljava/lang/String;): java.lang.NoSuchFieldError: no "Ljava/lang/String;" field "EFFECT_EMBOSS" in class "Landroid/hardware/Camera$Parameters;" or its superclasses
    java.lang.NoSuchFieldError: no "Ljava/lang/String;" field "EFFECT_EMBOSS" in class "Landroid/hardware/Camera$Parameters;" or its superclasses

```
- ~~1.20.0버전 작동 안되는듯 (확인안됨)~~
- androidmedia 플러그인문제로 확인
  - [참고](https://gitlab.freedesktop.org/gstreamer/cerbero/-/issues/283)
  - 안드로이드의 장치를 gstreamer에서 직접 사용하지 않을거라면 무시해도 되는 문제

- storage permission

- gstreamer android버전 다운로드 후 gradle.properties에 `gstAndroidRoot` 설정 또는 `GSTREAMER_ROOT_ANDROID` 환경변수 설정
  - gstAndroidRoot로 설정하는 경우 경로에 따옴표 넣으면 안됨!!

- 처음 안드로이드 프로젝트 생성시 템플릿에서 Native C++를 선택하면
CMake를 이용한 프로젝트가 생성되는데, [gst-docs](https://gitlab.freedesktop.org/gstreamer/gst-docs/) 를 참고하여 Android.mk로 빌드할 수 있도록 변경해줘야함 (Eclipse 쓸 경우 기본 세팅에서 약간 변경하면 되는듯)

- 자바 11쓰도록 프로젝트 설정
  1. `build.gradle` (:app) 에서
    - `JavaVersion.VERSION_1_8`을 `JavaVersion.VERSION_11`로 변경
    - `jvmTarget` `'11'`로 변경
  2. File > Project Structure > SDK Location 페이지 아래에 Gradle Settings 클릭 > 아래 Gradle JDK 자바 버전 11로 변경
  [참고1](https://blog.naver.com/PostView.naver?blogId=nakim02&logNo=222450115057&parentCategoryNo=&categoryNo=217&viewDate=&isShowPopularPosts=false&from=postView)
  [참고2](https://bacassf.tistory.com/143)

- ~~gst/gst.h 를 찾을 수 없을 경우 Android.mk에서 `LOCAL_C_INCLUDES`또는 `LOCAL_CFLAGS` 변수를 설정해줌~~
~~[참고](https://developer.android.com/ndk/guides/android_mk#mdv)~~
  - ~~이렇게만하면 gstreamer_android 컴파일할 때 헤더를 찾을 수 없는 경우가 있어서 `LOCAL_C_INCLUDES` 가 아닌 `C_INCLUDE_PATH`를 설정하고 export 해서 컴파일하는 모든 경우에서 include될 수 있도록 하는 방법도 필요할 듯~~
- 위의 문제는 `PKG_CONFIG_PATH` 를 설정하면 모두 해결됨

- ~~org.freedesktop.gstreamer.GStreamer 클래스를 찾을 수 없는 경우 일단 $(GSTREAMER_ROOT)/share/gst-android/ndk-build 에 있는 Gstreamer.java 파일을 패키지 구조에 맞게 프로젝트에 복사하는 방법을 사용 (수정 필요)~~
- 위의 방법을 사용하지 않아도 되고 대신 ndkBuild에서 `GSTREAMER_JAVA_SRC_DIR`을 src/main/java (실제 자바 소스가 들어가는 디렉토리)로 변경해주면 빌드시에 자동으로 자바파일 추가해줌 (프로젝트가 Eclipse기준이기 때문에 Android Studio에 맞게 수정해줘야됨)
  - `GSTREAMER_ASSETS_DIR`는 src/main/assets로 변경
    - **이때 저장공간에 read/write 하는 권한 필요**

- 기존 gstreamer android tutorial c 소스에 포함되어있는 `JNI_OnLoad`함수에서 JNIEnv에 함수를 등록하는 방식이 아닌 Java_<클래스경로 포함한 함수이름> 으로 함수를 정의하여 사용함
  - `JNI_OnLoad` 대소문자 주의
  - 사실 JNIEnv에 함수 등록해서 쓸려고 했는데 `JNI_OnLoad`함수가 안불리길래 봤더니 대소문자문제였음

- native코드에서 initialize하는 함수 안불러서 작동 안되고있었음

- android-tutorial-5의 AndroidManifest.xml에서 mimetype설정 참고

- h264 hardware decode의 경우 amcviddec-omxgoogleh264decoder

### LibVLC Hardware Acceleration (Decoding)
```kotlin
media.setHWDecoderEnabled(true, false)
```


## 2022-03-25

- [ ] send timestamp on cb_buffer
  - [ ] test


## References

[Fragment Transition](https://medium.com/@bherbst/fragment-transitions-with-shared-elements-7c7d71d31cbb)
[Alpine Term](https://github.com/ichit/alpine-term)
