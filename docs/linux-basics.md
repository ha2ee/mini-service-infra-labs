# Linux Basics

## 목적
이 문서는 Linux 환경에서 서버 상태를 점검할 때 자주 사용하는 기본 명령어와 확인 순서를 정리한다.

## 기본 점검 관점
서버에 문제가 생겼을 때 아래 순서로 확인한다.

1. 프로세스가 살아 있는가
2. 포트를 정상적으로 열고 있는가
3. HTTP 요청에 응답하는가
4. CPU, 메모리, 디스크에 이상이 있는가
5. 로그에 에러가 남는가

## 프로세스 확인

### 자주 쓰는 명령어
```bash
ps -ef | grep uvicorn
pgrep -af uvicorn
```
확인 포인트
- 앱 프로세스가 실행 중인지
- 예상한 프로세스 이름으로 떠 있는지

## 포트 확인

### 자주 쓰는 명령어
```bash
ss -lntp | grep 8000
```
확인 포인트
- 앱이 8000 포트를 리슨 중인지
- 다른 프로세스가 같은 포트를 쓰고 있지는 않은지

## HTTP 응답 확인

### 자주 쓰는 명령어
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
curl -i http://127.0.0.1:8000/error
```
확인 포인트
- `/health`가 200인지
- `/ready`가 설정에 따라 200 또는 503인지
- `/error`는 의도적으로 500을 반환하는지

## 리소스 확인

### 자주 쓰는 명령어
```bash
top
free -h
df -h
```
확인 포인트
- CPU 사용률이 비정상적으로 높지 않은지
- 메모리가 부족하지 않은지
- 디스크 사용량이 과도하지 않은지

## 로그 확인

### 현재 확인 방법
- 수동 실행 시 uvicorn을 실행한 터미널에서 요청 로그와 에러 로그를 확인한다.
- systemd 서비스 실행 시 `journalctl -u mini-service-app`으로 로그를 확인한다.

### 자주 쓰는 명령어
```bash
sudo journalctl -u mini-service-app -n 50
sudo journalctl -u mini-service-app -f
```
확인 포인트
- 서비스가 정상적으로 시작됐는지
- `/health`, `/ready` 요청이 실제로 들어왔는지
- 에러 발생 시 어떤 메시지가 남는지

## 현재 실습에서 자주 쓰는 점검 순서
```bash
sudo systemctl status mini-service-app
ss -lntp | grep 8000
ss -lntp | grep 8080
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8080/health
./scripts/health-check.sh
sudo journalctl -u mini-service-app -n 50
```

## 메모
- `/health`는 프로세스 생존 확인용이다.
- `/ready`는 준비 상태 확인용이다.
- readiness 실패와 프로세스 다운은 다르게 해석해야 한다.

## 서비스 상태 확인

### 자주 쓰는 명령어
```bash
sudo systemctl status mini-service-app
sudo systemctl restart mini-service-app
sudo systemctl enable mini-service-app
```
확인 포인트
- 서비스가 active (running) 상태인지
- 재시작이 필요한 상황인지
- 부팅 시 자동 시작이 설정되어 있는지