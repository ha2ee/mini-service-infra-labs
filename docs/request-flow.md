# Request Flow

## 목적
이 문서는 현재 실습 환경에서 HTTP 요청이 어떤 경로를 거쳐 전달되는지 정리한다.

## 현재 요청 흐름
Client -> Nginx -> App

## 구성 요약
- Client는 `curl` 또는 브라우저로 요청을 보낸다.
- Nginx는 `127.0.0.1:8080`에서 요청을 받는다.
- App은 `127.0.0.1:8000`에서 응답을 생성한다.

## 요청 예시: /health
1. Client가 `http://127.0.0.1:8080/health` 로 요청을 보낸다.
2. Nginx가 8080 포트에서 요청을 수신한다.
3. Nginx가 요청을 `http://127.0.0.1:8000/health`로 전달한다.
4. App이 200 응답을 반환한다.
5. Nginx가 응답을 Client에게 다시 반환한다.

## 현재 확인한 응답
- `/health` -> 200
- `/ready` -> 503
- `/error` -> 500
- `/slow` -> 200 (약 3초 지연)

## 로그에서 본 흐름
- access log에는 요청 경로와 상태코드가 기록된다.
- error log에는 upstream 연결 실패 같은 프록시 에러가 기록된다.
- app(uvicorn) 로그에는 실제 요청 처리 결과가 기록된다.

## 확인한 사례

### 1. upstream app이 실행되지 않은 경우
- Nginx access log: 502
- Nginx error log: `connect() failed (111: Connection refused)`
- 의미: Nginx는 요청을 받았지만 App으로 연결하지 못했다.

### 2. `/ready` 요청 시 503이 반환된 경우
- App이 `LAB_ENV is not set` 메시지와 함께 503을 반환했다.
- Nginx는 이 응답을 그대로 Client에게 전달했다.

### 3. `/error` 요청 시 500이 반환된 경우
- App이 의도적으로 500을 반환했다.
- Nginx는 이 응답을 그대로 Client에게 전달했다.

### 4. `/slow` 요청 중 클라이언트가 먼저 종료한 경우
- Nginx access log: 499
- 의미: 서버 에러가 아니라 클라이언트가 먼저 연결을 종료했다.

## 점검 포인트
- Nginx가 요청을 정상적으로 받고 있는가
- App이 8000 포트에서 실행 중인가
- App이 실제로 어떤 상태코드를 반환하는가
- access log, error log, app 로그가 서로 어떻게 대응되는가

## 메모
- 502는 Nginx가 upstream(App)과 연결하지 못한 경우에 발생할 수 있다.
- 503은 App이 준비되지 않았음을 의미할 수 있다.
- 500은 App 내부 에러 또는 의도적인 에러 응답일 수 있다.
- 499는 클라이언트가 먼저 연결을 끊은 경우에 기록될 수 있다.

