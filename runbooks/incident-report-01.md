# Incident Report 01 - Upstream App Down

## 개요
Nginx는 정상 실행 중이었지만, upstream App이 중지된 상태에서 요청을 보내 502 Bad Gateway를 재현했다.

## 장애 시점
- 실습 일시: 2026-03-21
- 환경: Ubuntu Server VM, Nginx -> FastAPI App

## 증상
- `curl http://127.0.0.1:8080/health` 요청 시 502 Bad Gateway 발생
- Swagger UI에서 `/health` 호출 시 FastAPI JSON 응답 대신 Nginx 기본 502 HTML 페이지가 반환됨

## 원인
- App 프로세스가 중지되어 Nginx가 upstream(127.0.0.1:8000)에 연결하지 못했다.

## 관측 내용

### access log
- `GET /health` -> 502
- 127.0.0.1 - - [21/Mar/2026:04:17:29 +0000] "GET /health HTTP/1.1" 502 166 "-" "curl/8.5.0"

### error log
- `connect() failed (111: Connection refused) while connecting to upstream`
- 의미: Nginx는 요청을 받았지만 App으로 연결하지 못했다.

## 확인 과정
1. 정상 상태에서 `/health` 200 응답 확인
2. App 프로세스를 중지했다.
3. Nginx 경유 `/health` 요청 시 502가 발생하는 것을 확인했다.
4. access log와 error log를 확인했다.
5. App 재기동 후 `/health`가 다시 200으로 복구되는 것을 확인했다.

## 복구 방법
- App 프로세스를 다시 실행한다.

## 배운 점
- Nginx가 살아 있어도 upstream App이 죽으면 502가 발생할 수 있다.
- access log와 error log를 같이 봐야 원인을 좁히기 쉽다.
- "접속 안 됨"은 Nginx 문제와 App 문제를 구분해서 봐야 한다.
- Nginx가 반환한 502 응답은 App JSON이 아니라 기본 HTML 에러 페이지일 수 있다.

## 다음 개선점
- App을 systemd 서비스로 등록해 자동 재시작 구조를 실험해볼 수 있다.
- `health-check.sh` 스크립트에 Nginx 경유 점검도 추가할 수 있다.