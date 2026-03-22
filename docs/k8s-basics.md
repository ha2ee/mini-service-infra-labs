# Kubernetes Basics

## 목적
이 문서는 mini-service-app을 kind 클러스터에 배포하면서 확인한 기본 Kubernetes 리소스와 점검 방법을 정리한다.

## 사용한 리소스
- ConfigMap
- Deployment
- Service

## 현재 구성
- kind 클러스터: `mini-labs`
- App 이미지: `mini-service-infra-labs-app:latest`
- ConfigMap: `LAB_ENV=local`
- Deployment: `mini-service-app`
- Service: `mini-service-app`

## 확인한 동작
- `/health` -> 200
- `/ready` -> 200
- `kubectl get pods`
- `kubectl get deployments`
- `kubectl get svc`
- `kubectl port-forward service/mini-service-app 18000:80`

## readiness 실패 재현
- Deployment에서 `LAB_ENV`를 빈 값으로 override했다.
- 새 Pod는 `0/1 Running` 상태가 되었고 `Ready=False`로 표시됐다.
- `kubectl describe pod`에서 `Readiness probe failed: HTTP probe failed with statuscode: 503` 이벤트를 확인했다.
- 새 Pod에 직접 `port-forward` 했을 때 `/health`는 200, `/ready`는 503을 반환했다.
- 기존 Ready Pod는 유지되어 Service 가용성이 계속 보장되는 것을 확인했다.

## 배운 점
- liveness와 readiness는 서로 다른 목적을 가진다.
- 프로세스가 살아 있어도 readiness는 실패할 수 있다.
- Kubernetes는 readiness에 실패한 새 Pod를 바로 서비스에 포함하지 않는다.
- rolling update 중에는 기존 Ready Pod와 새 NotReady Pod가 잠시 함께 존재할 수 있다.

## 기본 점검 명령어
```bash
kubectl get pods
kubectl get deployments
kubectl get svc
kubectl logs deployment/mini-service-app
kubectl describe pod <pod-name>
kubectl port-forward service/mini-service-app 18000:80
```
## 메모
- ConfigMap은 비민감 설정을 분리하는 데 사용했다.
- readinessProbe는 `/ready`, livenessProbe는 `/health`를 사용했다.
- Service는 Pod 앞의 고정된 접근점 역할을 한다.