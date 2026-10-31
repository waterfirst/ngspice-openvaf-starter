# GW 예제와 논문 주장: 검증 범위

## 대상 논문

Hwarim Im, Eun Kyo Jung, Shin-Hyeong Kim, Kook Chul Moon, Yong-Sang Kim,
“Oxide TFT-Based Scan Driver Circuit With Blocking Structure for Multisignal Output,”
*Journal of the Society for Information Display*, 2026, DOI:
[10.1002/jsid.70114](https://doi.org/10.1002/jsid.70114).

원문은 Wiley의 유료 Version of Record이다. 그래서 이 저장소에는 원문 PDF를 복제하지 않는다.
논문은 DOI 링크에서 합법적으로 열람해야 한다. 아래 내용은 공개 초록을 근거로 한 요약과
별도 합성 모델 시뮬레이션이다.

## 논문의 공개 초록이 말하는 것

1. 하나의 스테이지에서 여러 출력을 내되, **blocking structure**로 제어 노드를 분리해
   클록 간섭과 원치 않는 펄스를 줄인다.
2. 다중 출력으로 전력 소모가 42.3% 감소했다고 보고한다.
3. 회로 시뮬레이션에서 산화물 TFT의 문턱전압이 -1.6 V ~ +0.8 V일 때 안정 동작을
   보고한다.

공개 초록: [Wiley JSID](https://sid.onlinelibrary.wiley.com/doi/10.1002/jsid.70114)

## 이 저장소가 실제로 검증하는 것

`bash scripts/run_gw_example.sh`는 OpenVAF로 합성 NMOS TFT 모델을 컴파일하고,
ngspice OSDI에서 6단 complementary-TFT GW 체인을 과도해석한다. 통과 기준은 각 OUT1~OUT6에 자기
시간 슬롯의 펄스가 정확히 하나이고, 출력이 −8.5 V보다 낮게 내려가지 않으며 +7.5 V 이상 올라가는지다. 회로도는
[`gw_schematic.svg`](../figures/gw_schematic.svg), 실제 파형은
[`gw_6stage_actual_waveform.svg`](../figures/gw_6stage_actual_waveform.svg)에 있다.

### 검증 결과

- 기준 합성 카드(dVth = 0 V): 6개 슬롯 각각 1펄스, **PASS**.
- 같은 합성 카드에서 dVth = -1.6 V, 0 V, +0.8 V 모두 **PASS**였다. 전체 실행 표는
  [`gw_validation_result_ko.md`](gw_validation_result_ko.md)에 있다.
- 이 결과는 “순차 GW 펄스와 레일이 유지되는가”만 확인한다.
- 실제 측정값은 OUT1~OUT6의 max = +8.000 V, min = −8.021~−8.023 V이며,
  펄스는 15.560 µs부터 44.560 µs까지 5 µs 간격으로 한 번씩 나온다.

## 검증하지 않은 것

- 논문의 실제 blocking 구조는 유료 원문 회로도가 없어서 구현하거나 검증하지 않았다.
- 따라서 42.3% 전력 감소는 이 예제로 재현·주장하지 않는다.
- 논문의 -1.6 V ~ +0.8 V 범위도 동일 토폴로지·동일 산화물 카드가 아니므로 이 저장소가
  독립 검증한 값이 아니다. 이 예제의 `dVth` 인자는 **합성 모델 감도 탐색용**이다.

이 구분은 “동일 조건의 재현”과 “교육용 동작 예시”를 혼동하지 않기 위한 것이다.

## 특허 토폴로지 참고

교육용 래치+출력 경로의 출발점은 공개 특허
[KR20170071217A](https://patents.google.com/patent/KR20170071217A/ko)의 Figure 3이다.
이 저장소의 크기·부하·클록·합성 TFT 카드는 원문 수치를 뜻하지 않는다.
