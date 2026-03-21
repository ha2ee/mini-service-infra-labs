# Incident Report 02 - Wrong Upstream Port Configuration

## 개요
App은 정상 실행 중이었지만, Nginx의 `proxy_pass`가 잘못된 포트를 가리키도록 설정되어 502 Bad Gateway를 재현했다.

## 장애 시점
- 실습 일시: 2026-03-21
- 환경: Ubuntu Server VM, Nginx -> FastAPI App

## 증상
- `curl http://127.0.0.1:8080/health` 요청 시 502 Bad Gateway 발생
- `curl http://127.0.0.1:8000/health` 요청은 200 OK로 정상 응답
- 즉, App direct 경로는 정상이고 Nginx proxy 경로만 실패했다.

## 원인
- Nginx 설정에서 `proxy_pass`가 `http://127.0.0.1:8001`로 잘못 설정되어 있었다.
- 실제 App은 `127.0.0.1:8000`에서 실행 중이었다.

## 관측 내용

### health-check 스크립트 결과
- app direct `/health` -> 200
- nginx proxy `/health` -> 502

### curl 확인
- `http://127.0.0.1:8000/health` -> 200
- `http://127.0.0.1:8080/health` -> 502

### access log
- `GET /health` -> 502
- `GET /ready` -> 502

### error log
- `connect() failed (111: Connection refused) while connecting to upstream`
- `upstream: "http://127.0.0.1:8001/health"`
- 의미: Nginx는 요청을 받았지만 잘못된 upstream 포트로 연결을 시도했다.

## 확인 과정
1. 정상 상태에서 health-check 스크립트로 app과 nginx 모두 정상 응답을 확인했다.
2. Nginx 설정의 `proxy_pass`를 `127.0.0.1:8001`로 변경했다.
3. `nginx -t`로 문법 검사를 했고, 문법상 오류는 없음을 확인했다.
4. Nginx를 reload한 뒤 health-check를 다시 실행했다.
5. App direct는 200이었지만 nginx proxy는 502가 발생하는 것을 확인했다.
6. access log와 error log를 확인해 upstream 대상이 `8001`로 잘못 지정된 것을 확인했다.
7. `proxy_pass`를 다시 `127.0.0.1:8000`으로 수정하고 reload한 뒤 정상 복구를 확인했다.

## 복구 방법
- Nginx 설정의 `proxy_pass`를 올바른 upstream 주소(`127.0.0.1:8000`)로 수정한다.
- `sudo nginx -t`로 문법을 확인한다.
- `sudo systemctl reload nginx`로 설정을 반영한다.

## 배운 점
- 502는 항상 App down을 의미하지 않는다.
- App direct 경로와 Nginx proxy 경로를 분리해서 확인해야 원인을 정확히 좁힐 수 있다.
- `nginx -t`가 성공해도 런타임 연결 오류는 발생할 수 있다.
- 설정 문법이 맞는 것과 실제 연결 대상이 올바른 것은 다른 문제다.

## 다음 개선점
- runbook에 `app direct는 정상인데 proxy만 실패하면 upstream 설정을 확인한다`는 항목을 추가할 수 있다.
- health-check 스크립트 결과를 바탕으로 장애 분류 기준을 더 정리할 수 있다.