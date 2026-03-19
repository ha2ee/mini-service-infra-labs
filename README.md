# Mini Service Infra Labs

## 프로젝트 소개 
이 저장소는 Linux, 네트워크, 모니터링, Kubernetes, Redis, Kafka를 하나의 실습 환경에서 연결하며
장애 재현, 관찰, 복구, 자동화를 기록하기 위한 개인 인프라 학습 저장소입니다.
단순 설치나 개념 정리에 그치지 않고, 직접 문제를 만들고 로그/지표를 통해 원인을 좁혀가는 과정을 남깁니다.

## 디렉터리 구조
 - `architecture.md`: 전체 시스템 구조도 및 컴포넌트 연결 상태를 기록하는 문서
 - `docs/`: 리눅스, 네트워크, 미들웨어 등 핵심 개념과 학습 노트
 - `runbooks/`: 장애 대응 가이드(Runbook) 및 포스트모템(Incident Report) 기록
 - `scripts/`: 서버 점검 및 운영 자동화 스크립트 (Shell, Python)
 - `monitoring/`: Prometheus, Grafana 등 모니터링 설정 파일
 - `docker/`: Dockerfile 및 Docker Compose 등 컨테이너 관련 파일
 - `k8s/`: Kubernetes 배포용 매니페스트 파일
