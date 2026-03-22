# Kubernetes Basics

## 목적
이 문서는 mini-service-app을 kind 클러스터에 배포하면서 확인한 기본 Kubernetes 리소스와 점검 방법을 정리한다.

## 사용한 리소스
- ConfigMap
- Deployment
- Service

## 현재 구성
- kind 클러스터: `mini-lab`
- App 이미지: `mini-service-infra-labs-app:v1`, `mini-service-infra-labs-app:v2`
- ConfigMap: `LAB_ENV=local`
- Secret: `APP_SECRET_TOKEN`
- Deployment: `mini-service-app`
- Service: `mini-service-app`

## 확인한 동작
- `/health` -> 200
- `/ready` -> 200
- `kubectl get pods`
- `kubectl get deployments`
- `kubectl get svc`
- `kubectl port-forward service/mini-service-app 18000:80`

## Secret 적용 확인
- `Secret` 리소스를 생성하고 `APP_SECRET_TOKEN`을 Pod 환경변수로 주입했다.
- `/ready` 응답에 `secret_loaded: true`가 포함되는 것을 확인했다.
- `kubectl rollout status deployment/mini-service-app`으로 새 Deployment가 정상적으로 반영된 것을 확인했다.

## Rolling update / rollback 확인
- 앱 응답에 `version` 값을 추가하고 `v1`, `v2` 태그 이미지를 각각 빌드했다.
- Deployment 이미지 태그를 `v1`에서 `v2`로 변경한 뒤 `kubectl rollout status deployment/mini-service-app`으로 배포 완료를 확인했다.
- `kubectl rollout undo deployment/mini-service-app`으로 이전 revision으로 롤백했고, `/` 응답에서 다시 `version: v1`이 반환되는 것을 확인했다.
- `kubectl get deployment mini-service-app -o jsonpath='{.spec.template.spec.containers[0].image}'`로 현재 Deployment가 실제로 어떤 이미지 태그를 사용하는지도 확인했다.
- `latest` 같은 mutable tag는 rollback 실습에서 혼동을 만들 수 있으므로 `v1`, `v2` 같은 고정 태그를 사용하는 편이 더 명확했다.

## readiness 실패 재현
- Deployment에서 `LAB_ENV`를 빈 값으로 override했다.
- 새 Pod는 `0/1 Running` 상태가 되었고 `Ready=False`로 표시됐다.
- `kubectl describe pod`에서 `Readiness probe failed: HTTP probe failed with statuscode: 503` 이벤트를 확인했다.
- 새 Pod에 직접 `port-forward` 했을 때 `/health`는 200, `/ready`는 503을 반환했다.
- 기존 Ready Pod는 유지되어 Service 가용성이 계속 보장되는 것을 확인했다.

## ConfigMap key 참조 오류 재현
- Deployment의 `configMapKeyRef.key`를 `LAB_ENV_WRONG`으로 변경했다.
- Pod는 `CreateContainerConfigError` 상태가 되었고 컨테이너가 시작되지 않았다.
- `kubectl describe pod`에서 `couldn't find key LAB_ENV_WRONG in ConfigMap default/mini-service-app-config` 이벤트를 확인했다.
- 이 경우에는 readiness probe까지 가지 못하고, 컨테이너 설정 단계에서 바로 실패한다.
- `RollingUpdate` 중 기존 Ready Pod는 유지되어 Service 가용성이 계속 보장되는 것을 확인했다.

## Secret key 참조 오류 재현
- Deployment의 `secretKeyRef.key`를 `APP_SECRET_TOKEN_WRONG`으로 변경했다.
- 새 Pod는 `CreateContainerConfigError` 상태가 되었고 컨테이너가 시작되지 않았다.
- `kubectl describe pod`에서 `couldn't find key APP_SECRET_TOKEN_WRONG in Secret default/mini-service-app-secret` 이벤트를 확인했다.
- 이 경우에도 readiness probe까지 가지 못하고, 컨테이너 설정 단계에서 바로 실패한다.
- rolling update 중 기존 Ready Pod는 유지되어 Service 가용성이 계속 보장되는 것을 확인했다.

## 배운 점
- liveness와 readiness는 서로 다른 목적을 가진다.
- 프로세스가 살아 있어도 readiness는 실패할 수 있다.
- Kubernetes는 readiness에 실패한 새 Pod를 바로 서비스에 포함하지 않는다.
- `RollingUpdate` 중에는 기존 Ready Pod와 새 NotReady Pod가 잠시 함께 존재할 수 있다.
- rollout과 rollback 실습은 `latest`보다 고정 버전 태그를 사용할 때 더 예측 가능하게 동작한다.
- ConfigMap 참조 오류는 readiness 실패 이전 단계에서 `CreateContainerConfigError`로 나타날 수 있다.
- Secret은 Pod 환경변수로 주입할 수 있고, 잘못된 참조는 컨테이너 시작 실패로 이어질 수 있다.
- Secret 참조 오류도 ConfigMap 참조 오류와 마찬가지로 `CreateContainerConfigError`를 만들 수 있다.

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
