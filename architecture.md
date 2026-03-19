# Architecture

## 목적
이 문서는 현재 실습 환경의 구성과 각 컴포넌트의 역할, 요청 흐름, 관측 포인트를 정리합니다.

## 현재 구성
Client -> Nginx -> App

## 구성 요소
- Client: curl 또는 브라우저로 요청을 보내는 주체
- Nginx: reverse proxy, 요청 수신 및 라우팅
- App: 간단한 HTTP API 제공, health check 및 장애 재현 엔드포인트 포함 예정

## 요청 흐름
1. Client가 Nginx로 요청을 보낸다.
2. Nginx가 App으로 프록시한다.
3. App이 응답을 반환한다.
4. 장애 발생 시 Nginx 로그와 App 로그를 우선 확인한다.

## 관측 포인트
- Nginx access/error log
- App stdout/stderr 또는 systemd journal
- 서버 CPU, 메모리, 디스크, 포트 상태

## 예정된 확장
- Prometheus / Grafana 추가
- Redis 연결
- Kafka 실습 환경 연결
- Kubernetes 배포로 확장

## 예정된 장애 시나리오
- upstream app down
- 잘못된 포트 설정
- readiness 실패