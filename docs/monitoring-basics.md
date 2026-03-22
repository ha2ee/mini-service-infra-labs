# Monitoring Basics

## 목적
이 문서는 Prometheus, node-exporter, Grafana를 이용해 mini-service-infra-lab 환경의 기본 시스템 메트릭을 수집하고 시각화한 내용을 정리한다.

## 구성 요소
- Prometheus: 메트릭 수집
- node-exporter: 호스트 시스템 메트릭 노출
- Grafana: 메트릭 시각화

## 실행 환경
- Prometheus: `http://<VM-IP>:19090`
- Grafana: `http://<VM-IP>:13000`
- Alertmanager: `http://<VM-IP>:19093`

## 확인한 동작
- Prometheus Targets에서 `prometheus`, `node-exporter`가 모두 `UP`으로 표시됨
- Grafana에서 Prometheus 데이터소스 연결 성공
- Grafana Explore에서 `up` 쿼리 결과가 1로 표시됨
- Node Exporter Full 대시보드에서 CPU, 메모리, 디스크, 네트워크 지표 확인

## Alertmanager 연동 확인
- Prometheus에 `alerting` 설정을 추가하고 Alertmanager를 monitoring compose에 포함했다.
- `InstanceDown` 알람이 `firing` 상태가 되면 Alertmanager UI에서도 해당 알람이 수신되는 것을 확인했다.
- Alertmanager는 `alertname`, `job` 기준으로 alert를 묶어 보여주었다.
- Prometheus와 Alertmanager UI 모두 상태 변경 후 새로고침으로 확인했다.

## 기본 알람 확인
- Prometheus alert rule 파일에 `InstanceDown` 규칙을 추가했다.
- 조건은 `up == 0` 이고, 1분 이상 지속되면 `warning` 알람이 발생하도록 설정했다.
- `node-exporter`를 중지한 뒤 Prometheus UI의 `Alerts` 탭에서 `InstanceDown`이 `firing` 상태로 바뀌는 것을 확인했다.
- `node-exporter`를 다시 시작한 뒤 알람이 `inactive` 상태로 돌아오는 것도 확인했다.

## 기본 점검 방법
- Prometheus UI: `Status -> Target health`
- Grafana Data source: `Save & test`
- Grafana Explore: `up`
- Grafana Dashboard: Node Exporter Full

## 메모
- `up == 1`은 target scrape 성공을 의미한다.
- Prometheus는 수집, Grafana는 시각화를 담당한다.
- node-exporter는 호스트 시스템 메트릭을 Prometheus 형식으로 노출한다.

