# Kafka KRaft Lab

## 목적
이 문서는 Kafka 단일 브로커 KRaft 환경을 Docker Compose로 실습하면서 topic, producer/consumer, consumer group, offset, lag, broker down 시나리오를 확인한 내용을 정리한다.

## 구성
- Kafka single broker
- KRaft combined mode (`broker,controller`)
- 단일 topic 실습
- consumer group offset 확인

관련 파일:
- [compose.yaml](/home/master/projects/mini-service-infra-labs/kafka/compose.yaml)
- [server.properties](/home/master/projects/mini-service-infra-labs/kafka/config/server.properties)

## KRaft를 사용하는 이유
- 최근 Kafka 실습은 ZooKeeper 대신 KRaft 모드를 기준으로 보는 흐름이 자연스럽다.
- 이번 실습은 단일 브로커 환경이므로 `broker,controller` combined mode로 구성했다.
- 학습 목적상 작은 환경에서는 combined mode가 단순하고 이해하기 쉽다.

## 확인한 동작
- `lab-topic` topic을 생성하고 목록에서 확인했다.
- producer로 `hello kafka`, `message one`, `message two` 등의 메시지를 topic에 기록했다.
- consumer로 topic 데이터를 읽을 수 있는 것을 확인했다.
- `--group lab-group`으로 consumer group을 만들어 consume할 수 있는 것을 확인했다.

## topic / producer / consumer 확인
- `kafka-topics.sh --create`로 `lab-topic`을 생성했다.
- `kafka-console-producer.sh`로 메시지를 발행했다.
- `kafka-console-consumer.sh --from-beginning`으로 처음부터 메시지를 읽었다.
- 이를 통해 broker, topic, producer, consumer의 기본 흐름을 확인했다.

## consumer group / offset / lag 확인
- `kafka-console-consumer.sh --group lab-group`으로 consumer group 기반 consume을 실행했다.
- `kafka-consumer-groups.sh --describe --group lab-group`으로 group 상태를 확인했다.
- `CURRENT-OFFSET`은 consumer group이 현재까지 읽은 위치를 의미한다.
- `LOG-END-OFFSET`은 topic partition의 가장 끝 메시지 위치를 의미한다.
- `LAG`는 아직 consumer group이 처리하지 못한 메시지 수를 의미한다.

## lag 실습
- consumer group을 중지한 상태에서 producer로 `lag-test-one`, `lag-test-two`, `lag-test-three` 메시지를 추가했다.
- 이때 `CURRENT-OFFSET=7`, `LOG-END-OFFSET=10`, `LAG=3` 상태를 확인했다.
- consumer group을 다시 실행한 뒤 새 메시지를 읽고, 다시 확인했을 때 `CURRENT-OFFSET=10`, `LOG-END-OFFSET=10`, `LAG=0` 상태를 확인했다.
- 이를 통해 consumer가 멈추면 lag가 증가하고, 다시 consume하면 lag가 줄어드는 흐름을 확인했다.

## 장애 시나리오: broker down
- Kafka broker 컨테이너를 중지했을 때 단일 브로커 환경에서는 topic 조회, producer, consumer 기능이 모두 영향을 받는다는 점을 확인했다.
- broker를 다시 시작한 뒤 `lab-topic`과 `__consumer_offsets` 토픽이 보이는 것을 확인했다.
- 재기동 로그에서 consumer group metadata와 offsets 관련 상태가 다시 로드되는 흐름을 확인했다.

## 배운 점
- Kafka에서 topic은 메시지 저장 단위이고, consumer group은 읽기 상태를 offset으로 관리한다.
- `LAG`는 단순 숫자가 아니라 "아직 처리하지 못한 메시지 양"이라는 운영 지표로 볼 수 있다.
- 단일 브로커 Kafka는 broker down 시 전체 메시징 기능이 중단될 수 있으므로 고가용성이 없다.
- `__consumer_offsets`는 consumer group offset 상태를 관리하는 내부 토픽이다.
- KRaft는 ZooKeeper 없이 Kafka 메타데이터를 관리하는 최신 구성 방식이다.

## 다음에 더 볼 것
- partition 수를 늘렸을 때 consumer group 동작 변화
- broker replication이 있는 다중 브로커 구성
- broker down 시나리오에서 replication이 있을 때의 차이
