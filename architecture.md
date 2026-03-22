# Architecture

## 목적
이 문서는 현재 실습 환경의 구성과 각 컴포넌트의 역할, 요청 흐름, 관측 포인트를 정리합니다.

## 현재 구성
현재 실습 환경은 하나의 앱을 여러 실행 방식으로 다루는 구조입니다.

- VM 환경: Client -> Nginx -> App(systemd)
- Docker Compose 환경: Client -> Nginx container -> App container
- Kubernetes 환경: Client -> Service -> App Pod
- Monitoring 환경: Prometheus -> node-exporter, Prometheus -> Grafana

즉 이 저장소는 "같은 앱을 VM, Docker Compose, Kubernetes에서 실행하고, Prometheus와 Grafana로 관측하는 구조"를 기준으로 확장되고 있습니다.

## 구성 요소
- Client: curl 또는 브라우저로 요청을 보내는 주체
- Nginx: reverse proxy. VM 환경에서는 `127.0.0.1:8080`에서 요청을 받고 `127.0.0.1:8000`의 App으로 프록시한다. Docker Compose 환경에서는 Nginx 컨테이너가 `app:8000`으로 요청을 전달한다.
- App: FastAPI 기반 HTTP API. `/`, `/health`, `/ready`, `/slow`, `/error` 엔드포인트를 제공한다. `/ready`는 `LAB_ENV`와 `APP_SECRET_TOKEN`이 모두 있어야 정상 응답한다. `/`는 현재 배포 버전 확인용 `version` 값을 반환한다.
- Kubernetes: kind 기반 로컬 클러스터에서 App을 `Deployment`, `Service`, `ConfigMap`, `Secret`으로 배포한다.
- Prometheus: 메트릭 수집과 alert rule 평가를 담당한다.
- node-exporter: VM의 CPU, 메모리, 디스크, 네트워크 메트릭을 Prometheus 형식으로 노출한다.
- Grafana: Prometheus 데이터소스를 이용해 대시보드와 Explore 쿼리를 제공한다.

## 포트 구성
- VM 실행 시:
  - Nginx: `127.0.0.1:8080`
  - App: `127.0.0.1:8000`
- Docker Compose 실행 시:
  - Host: `127.0.0.1:18080`
  - Nginx container: `80`
  - App container: `8000`
- Kubernetes 실행 시:
  - App Service: cluster-internal `80 -> 8000`
  - 점검 시 `kubectl port-forward service/mini-service-app 18000:80`
- Monitoring 실행 시:
  - Prometheus: `http://<VM-IP>:19090`
  - Grafana: `http://<VM-IP>:13000`
  - node-exporter: `9100` on host network

## 요청 흐름
### VM / Docker Compose 요청 흐름
1. Client가 Nginx로 요청을 보낸다.
2. Nginx가 App으로 프록시한다.
3. App이 응답을 반환한다.
4. 장애 발생 시 Nginx 로그와 App 로그를 우선 확인한다.

추가 메모:
- VM 환경에서는 `127.0.0.1:8080 -> 127.0.0.1:8000` 흐름으로 동작한다.
- Docker Compose 환경에서는 `127.0.0.1:18080 -> nginx container -> app:8000` 흐름으로 동작한다.

### Kubernetes 요청 흐름
1. Client가 `kubectl port-forward`를 통해 Service로 요청을 보낸다.
2. Service가 label selector로 App Pod에 트래픽을 전달한다.
3. App Pod는 `readinessProbe`와 `livenessProbe`를 통해 상태를 노출한다.
4. readiness 실패 시 Pod는 살아 있어도 Service 트래픽 대상에서 제외될 수 있다.

### 모니터링 흐름
1. node-exporter가 VM 메트릭을 `/metrics`로 노출한다.
2. Prometheus가 주기적으로 `prometheus`와 `node-exporter` 타겟을 scrape한다.
3. Grafana가 Prometheus를 데이터소스로 사용해 지표를 시각화한다.
4. Prometheus alert rule은 `up == 0` 같은 조건을 평가해 알람 상태를 만든다.

## 관측 포인트
- Nginx access/error log
- App stdout/stderr 또는 uvicorn 로그
- systemd 환경에서는 `journalctl -u mini-service-app`
- 서버 CPU, 메모리, 디스크, 포트 상태
- Docker Compose 환경에서는 `docker compose logs`
- Kubernetes 환경에서는 `kubectl logs`, `kubectl describe pod`, `kubectl get events`
- Prometheus UI의 `Status -> Target health`
- Prometheus UI의 `Alerts`
- Grafana Explore의 `up` 쿼리 결과
- Grafana Node Exporter Full 대시보드

## 현재 확인된 동작
- `/health`는 200을 반환한다.
- `/ready`는 `LAB_ENV` 또는 `APP_SECRET_TOKEN`이 없으면 503을 반환하고, 둘 다 있으면 200을 반환한다.
- `/error`는 의도적으로 500을 반환한다.
- `/slow`는 약 3초 지연 후 200을 반환한다.
- Docker Compose 환경에서도 `/health`, `/ready`, `/error` 요청이 정상적으로 전달되는 것을 확인했다.
- Kubernetes 환경에서 `ConfigMap`, `Secret`, `Deployment`, `Service`를 이용해 앱을 배포하고 `/health`, `/ready` 동작을 확인했다.
- `readinessProbe` 실패, 잘못된 ConfigMap key, 잘못된 Secret key 시나리오를 재현했다.
- `v1 -> v2 -> v1` 롤링 업데이트와 rollback을 확인했다.
- Prometheus Targets에서 `prometheus`, `node-exporter`가 `UP`으로 표시되는 것을 확인했다.
- Grafana Explore에서 `up == 1` 결과를 확인했고, Node Exporter Full 대시보드에서 CPU, 메모리, 디스크, 네트워크 지표를 확인했다.
- `InstanceDown` alert rule로 `node-exporter` 중지 시 `firing`, 재기동 시 `inactive` 흐름을 확인했다.

## 다음 확장
- Alertmanager 또는 Grafana Alerting 연동
- 추가 Prometheus alert rule 작성
- `scripts/ops-check.py` 작성
- Redis 연결
- Kafka 실습 환경 연결
- Kubernetes requests/limits, StatefulSet 관점 보강

## 다음 장애 시나리오
- disk usage threshold 초과 알람
- HTTP 5xx 증가 감지
- Redis 연결 실패
- Kafka consumer 지연
