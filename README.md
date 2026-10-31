# ngspice + OpenVAF 간단 회로 시뮬레이션 안내

> 바로 실행할 예제는 두 개다. 저항 분압기와 6단 GW(게이트 파형) 펄스 체인이다.

GitHub Pages 보고서는 [`index.html`](index.html)이다.

## 예제 목록

1. **저항 분압기** — Verilog-A 저항 모델을 OSDI로 만들고, 1 V 입력에서 0.5 V 출력인지 확인한다.
2. **6단 GW 펄스 체인** — 합성 oxide-NMOS TFT 모델을 OSDI로 만들고, OUT1~OUT6이
   순서대로 한 번씩 펄스가 나오는지 검사한다.

## 처음 사용하는 사람: PMOS·NMOS 카드부터 확인

`models/tft.va`는 공통 3단자 TFT Verilog-A 모델이고,
`models/tft_cards.json`에는 아래 두 개의 **교육용 합성 25 °C 카드**가 들어 있다.

- `ltps_pmos_25c`: PMOS형 LTPS 카드
- `oxide_nmos_25c`: NMOS형 oxide TFT 카드

아래 한 줄을 먼저 실행해 두 카드가 모두 켜지는지 확인한다.

```bash
bash scripts/run_tft_iv.sh
```

정상이라면 두 카드 모두 I–V sweep의 끝점 전류가 시작점보다 100배 이상 크다는
`PASS`가 나온다. NMOS는 source=0 V에서 `Vg: 0→4 V`, PMOS는 source=+5 V에서
`Vg: +5→+1 V`로 바이어스한다. 결과 파일은 `results/nmos_iv.dat`, `results/pmos_iv.dat`에 생긴다.
이 카드들은 공개 교육용 합성 값이며, 실제 패널·제품의 측정 모델이 아니다.

GW 회로도와 5프레임 기준 파형, 논문 주장과 검증 범위는
[`docs/paper_and_verification_ko.md`](docs/paper_and_verification_ko.md)에 있다.
실제 문턱전압 스윕 결과는 [`docs/gw_validation_result_ko.md`](docs/gw_validation_result_ko.md)에 있다.

Ubuntu에서 Verilog-A 모델을 OpenVAF로 컴파일하고, ngspice OSDI로 불러
간단한 회로를 시뮬레이션하는 최소 예제다.

이 예제는 1 V 전원과 1 kOhm 저항 두 개로 만든 분압 회로를 실행한다.
예상 결과는 V(out) = 0.5 V, I(V1) = -0.5 mA다.

## 준비물

- Ubuntu 22.04 이상 권장, **x86_64 Linux**
- 인터넷 연결과 sudo 권한
- 약 2 GB 여유 공간

> Windows와 macOS는 이 안내의 대상이 아니다. OSDI 라이브러리는 운영체제와
> CPU 아키텍처가 맞아야 한다.

## 1. 기본 프로그램 설치

터미널을 열고 아래를 실행한다.

\`\`\`bash
sudo apt update
sudo apt install -y git curl ca-certificates build-essential \\
  autoconf automake libtool bison flex \\
  libreadline-dev libxaw7-dev libxmu-dev libxt-dev
\`\`\`

확인:

\`\`\`bash
git --version
gcc --version
\`\`\`

## 2. OSDI 지원 ngspice 설치

이 예제는 Verilog-A를 컴파일한 .osdi 파일을 사용한다. 따라서 일반
ngspice가 아니라 **--enable-osdi와 --enable-predictor 옵션으로 빌드한
ngspice**가 필요하다.

### 2-1. 소스 내려받기와 빌드

\`\`\`bash
mkdir -p ~/src
git clone https://github.com/imr/ngspice.git ~/src/ngspice
cd ~/src/ngspice
./autogen.sh
mkdir -p build && cd build
../configure --prefix="$HOME/.local" \\
  --enable-osdi --enable-predictor --enable-xspice --with-readline=yes
make -j"$(nproc)"
make install
\`\`\`

현재 터미널에서 새 ngspice를 사용한다.

\`\`\`bash
export PATH="$HOME/.local/bin:$PATH"
command -v ngspice
ngspice -v
\`\`\`

새 터미널에서도 자동으로 쓰려면 다음을 한 번 실행하고 터미널을 다시 연다.

\`\`\`bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
\`\`\`

unknown command pre_osdi 오류가 나오면 OSDI 없는 ngspice다. 위 2-1을 다시
진행하고, 예전에 설치한 시스템 ngspice가 먼저 실행되지 않는지
command -v ngspice로 확인한다.

자세한 빌드 플래그는
[ngspice OSDI 공식 문서](https://github.com/imr/ngspice/blob/master/README_OSDI.md)를 참고한다.

## 3. OpenVAF 설치

OpenVAF는 Verilog-A 파일(.va)을 ngspice가 읽을 수 있는 OSDI 파일(.osdi)로
변환한다.

1. [OpenVAF 공식 설치 페이지](https://openvaf.github.io/docs/getting-started/installation/)에서
   Linux x86_64 사전 빌드 실행 파일을 내려받는다.
2. 다운로드한 파일 이름이 openvaf라고 가정하고 실행한다.

\`\`\`bash
mkdir -p ~/.local/bin
install -m 0755 ~/Downloads/openvaf ~/.local/bin/openvaf
export PATH="$HOME/.local/bin:$PATH"
openvaf --help
\`\`\`

openvaf: command not found가 나오면 다운로드 파일 이름과 경로를 확인한다.
새 터미널에서도 쓰려면 2-1의 PATH 설정이 필요하다.

## 4. 예제 내려받기와 실행

\`\`\`bash
git clone https://github.com/waterfirst/ngspice-openvaf-starter.git
cd ngspice-openvaf-starter
bash scripts/run_example.sh
\`\`\`

성공하면 마지막 줄이 다음처럼 나온다.

\`\`\`text
PASS: V(out) = 0.5 V
\`\`\`

실행 과정은 다음과 같다.

1. models/ohmic.va를 OpenVAF로 컴파일한다.
2. build/ohmic.osdi가 만들어진다.
3. circuits/ohmic_divider.cir의 pre_osdi가 모델을 먼저 불러온다.
4. ngspice가 DC 동작점(op)을 계산한다.
5. 결과는 results/ohmic_divider.log에 저장된다.

## 5. 파일별 역할

\`\`\`text
models/ohmic.va             수정할 Verilog-A 저항 모델
circuits/ohmic_divider.cir  1 V / 1 kOhm + 1 kOhm 분압 회로
scripts/build_model.sh      .va -> .osdi 컴파일
scripts/run_example.sh      빌드 + ngspice 실행 + 0.5 V 판정
build/                      자동 생성 모델 파일
results/                    자동 생성 실행 로그
\`\`\`

## 6. 직접 바꿔 보기

circuits/ohmic_divider.cir의 모델 카드 값을 2k로 바꾼다.

\`\`\`spice
.model rmodel ohmic R=2k
\`\`\`

그 뒤 다시 실행한다.

\`\`\`bash
bash scripts/run_example.sh
\`\`\`

두 저항이 모두 같은 2 kOhm이면 출력은 계속 0.5 V다. 서로 다른 저항을 쓰려면
rmodel1, rmodel2처럼 모델 카드를 두 개 만들고 각 N 소자에 각각 연결하면 된다.

## 보안과 라이선스

- 이 저장소는 교육용 로컬 예제다. 네트워크 서버로 열지 않는다.
- 낯선 Verilog-A 모델이나 netlist는 실행하지 마라. 시뮬레이터도 파일을 읽고
  계산 자원을 사용한다.
- 이 저장소의 예제 코드는 MIT License다. ngspice와 OpenVAF의 라이선스는
  각각의 공식 저장소에서 확인한다.
