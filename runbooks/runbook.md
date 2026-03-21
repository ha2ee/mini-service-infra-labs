# Runbook

## 목적
이 문서는 mini-service-infra-lab 환경에서 App 또는 Nginx proxy 경로에 문제가 생겼을 때 기본적으로 확인할 절차를 정리한다.

## 대상 서비스
- App: FastAPI 기반 실습용 HTTP 서비스
- Nginx: reverse proxy. `127.0.0.1:8080`에서 요청을 받아 App으로 전달한다.
- App direct 주소: `http://127.0.0.1:8000`
- Nginx proxy 주소: `http://127.0.0.1:8080`

## 주요 엔드포인트
- `/health`: 프로세스 생존 확인
- `/ready`: 준비 상태 확인
- `/slow`: 지연 응답 테스트
- `/error`: 의도적인 500 에러 테스트

## 기본 점검 순서

### 1. App direct 응답 확인
```bash
curl http://127.0.0.1:8000/health
```

기대 결과:
- `200 OK`

### 2. Nginx proxy 응답 확인
```bash
curl http://127.0.0.1:8080/health
```

기대 결과:
- `200 OK`

### 3. 준비 상태 확인
```bash
curl http://127.0.0.1:8000/ready
curl http://127.0.0.1:8080/ready
```

기대 결과:
- `200 OK`
- 현재 설정에 따라 `503 Service Unavailable`

확인 포인트:
- `LAB_ENV` 환경변수 미설정 시 `503`이 발생할 수 있다.

### 4. 헬스체크 스크립트 실행
```bash
./scripts/health-check.sh
```

확인 포인트:
- app direct `/health`가 200인지
- nginx proxy `/health`가 200인지
- `/ready`가 200 또는 503인지

해석:
- app direct와 nginx proxy가 모두 실패하면 App down 가능성을 확인한다.
- app direct는 정상인데 nginx proxy만 실패하면 upstream 설정 문제를 확인한다.
- `/ready`만 503이면 App은 살아 있지만 준비 상태가 실패한 것일 수 있다.

### 5. App 프로세스 확인
```bash
ps -ef | grep uvicorn
```

확인 포인트:
- uvicorn 프로세스가 실행 중인지

### 6. 포트 리슨 상태 확인
```bash
ss -lntp | grep 8000
ss -lntp | grep 8080
```

확인 포인트:
- App이 8000 포트를 리슨 중인지
- Nginx가 8080 포트를 리슨 중인지

### 7. Nginx 설정 확인
확인 파일:
- `/etc/nginx/sites-available/mini-service-infra-labs`

확인 명령어:
```bash
sudo nginx -t
```

확인 포인트:
- `proxy_pass`가 올바른 upstream(`127.0.0.1:8000`)을 가리키는지
- 문법 오류가 없는지

### 8. 로그 확인
확인 대상:
- uvicorn 실행 터미널 로그
- `/var/log/nginx/access.log`
- `/var/log/nginx/error.log`

확인 포인트:
- `/health`, `/ready`, `/error` 요청이 실제로 들어왔는지
- 502, 503, 500이 어떤 경로에서 발생했는지
- `connect() failed` 같은 upstream 연결 에러가 있는지

## 자주 볼 수 있는 증상과 해석

### app direct와 nginx proxy가 모두 실패하는 경우
가능한 원인:
- App 프로세스가 실행되지 않음
- App이 잘못된 포트에서 실행 중임

확인 방법:
- `ps -ef | grep uvicorn`
- `ss -lntp | grep 8000`

### app direct는 정상인데 nginx proxy만 실패하는 경우
가능한 원인:
- Nginx의 `proxy_pass` 설정 오류
- 잘못된 upstream 포트 또는 주소 설정

확인 방법:
- `/etc/nginx/sites-available/mini-service-infra-labs`
- `sudo nginx -t`
- `sudo tail -n 20 /var/log/nginx/error.log`

### `/ready`가 503인 경우
가능한 원인:
- `LAB_ENV` 환경변수가 설정되지 않음
- readiness 조건을 만족하지 못함

해석:
- App 프로세스가 죽은 것은 아닐 수 있다.
- `/health`와 `/ready` 결과를 함께 봐야 한다.

### `/error`가 500인 경우
설명:
- 의도적으로 만든 장애 재현용 엔드포인트
- 현재는 정상적인 실습 동작

## 복구 초안
- App 프로세스가 중지된 경우 App을 재실행한다.
- app direct는 정상인데 nginx proxy만 실패하면 Nginx `proxy_pass` 설정을 확인한다.
- Nginx 설정 수정 후 `sudo nginx -t`로 검증한다.
- 설정이 올바르면 `sudo systemctl reload nginx`로 반영한다.
- `curl`과 `./scripts/health-check.sh`로 복구를 확인한다.
