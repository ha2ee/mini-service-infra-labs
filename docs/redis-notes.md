# Redis Notes

## 목적
이 문서는 Redis primary/replica 구성을 Docker Compose로 실습하면서 persistence, replication, 장애 시나리오를 확인한 내용을 정리한다.

## 구성
- Redis primary 1개
- Redis replica 1개
- primary data volume
- replica data volume

관련 파일:
- [compose.yaml](/home/master/projects/mini-service-infra-labs/redis/compose.yaml)
- [redis.conf](/home/master/projects/mini-service-infra-labs/redis/primary/redis.conf)
- [redis.conf](/home/master/projects/mini-service-infra-labs/redis/replica/redis.conf)

## 확인한 동작
- `redis-primary`에서 `SET lab:key "hello-redis"` 실행 후 `GET lab:key`로 값을 확인했다.
- `redis-replica`에서 동일한 key를 조회했을 때 `"hello-redis"`가 반환되는 것을 확인했다.
- `INFO replication` 결과에서 replica의 `role:slave`, `master_host:redis-primary`, `master_link_status:up`, `slave_read_only:1` 상태를 확인했다.
- `redis-primary`를 재시작한 뒤에도 `GET lab:key` 결과가 유지되는 것을 확인했다.

## persistence 확인
- primary 설정에서 `appendonly yes`, `appendfsync everysec`를 사용했다.
- Redis 컨테이너를 재시작한 뒤에도 key가 유지되는 것을 통해 persistence가 동작하는 것을 확인했다.
- 현재 실습은 AOF와 volume 기반 데이터 유지 흐름을 확인하는 데 초점을 두었다.

## replication 확인
- replica 설정에서 `replicaof redis-primary 6379`를 사용했다.
- primary에 기록한 key가 replica에서 조회되는 것을 통해 복제가 정상 동작하는 것을 확인했다.
- `INFO replication` 결과에서 replica가 primary와 정상 연결된 상태를 확인했다.

## 장애 시나리오: primary down
- `redis-primary`를 중지한 뒤 replica에서 `INFO replication`을 확인했다.
- 이때 `master_link_status:down` 상태를 확인했다.
- replica는 기존 key를 계속 읽을 수 있었다.
- replica에 `SET another:key "test"`를 시도하면 `READONLY You can't write against a read only replica.` 에러가 발생했다.

## 배운 점
- Redis replication은 primary의 데이터를 replica로 복제하지만, 자동 failover를 보장하지는 않는다.
- replica는 기본적으로 read-only 상태이므로 primary가 내려가도 자동으로 writable primary 역할을 하지 않는다.
- persistence와 replication은 서로 다른 목적을 가진다.
- persistence는 재시작 이후 데이터 유지에 가깝고, replication은 복제본 유지와 읽기 분산 관점에 가깝다.

## 다음에 더 볼 것
- Redis persistence 옵션 차이(RDB vs AOF) 정리
- replica promotion 또는 Sentinel 개념 정리
- 캐시 만료 정책과 eviction 동작 실험
