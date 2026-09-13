# 오프라인 점검의 WAL 검증 근거

2026-09-13. 실제 반례는 `phase80_wal_failure.json`과 `phase80_wal_corruption_before.log`에 있다. 정상 WAL에는 assignment/Run 미완료 기록이 있지만, 복사본 WAL의 magic 한 바이트를 바꾸면 SQLite가 checkpoint된 본체만 읽어 초기 빈 상태를 반환했다. 원본 파일은 수정하지 않았다.

SQLite의 WAL은 header와 누적 checksum·salt로 연결된 page frame을 저장한다. commit marker와 유효 prefix를 사용하며, reset 뒤 이전 세대의 frame이 끝에 남을 수 있다. 형식과 checksum 설명은 [공식 Database File Format §4](https://www.sqlite.org/fileformat2.html#walformat), 복구 시 첫 invalid checksum에서 멈추는 동작은 [공식 WAL File Format §3](https://www.sqlite.org/walformat.html)에 근거한다. 현재 bundled SQLite의 `walIndexRecover`/`walDecodeFrame`도 함께 검토했다.

RX 판단: SQLite의 읽기 성공·quick_check만으로 보존 원장의 전체 현재성을 확인했다고 표시하지 않는다. 복사된 비어 있지 않은 WAL을 SQLite보다 먼저 검사한다. 잘못된 header/구조/checksum은 거부하고, 재사용·미완료 쓰기·손상을 구분할 수 없는 tail은 `WAL_TAIL_UNPROVEN`으로 거부한다. 합법적인 재사용 tail을 손상이라고 단정하지 않는다. 원본을 truncate/repair하지 않는다.

이 검사는 비어 있지 않은 보존 WAL의 형식·연결성 검증이다. WAL 전체의 삭제/0바이트 절단 또는 main+WAL을 함께 과거 버전으로 되돌린 사실까지 독립적으로 증명할 수는 없다. SQLite checksum은 외부의 신뢰된 마지막 commit 번호나 암호학적 감사 원장을 대신하지 않는다. 그런 최신성/복원 증거가 필요한 경우 별도 저장 세대·복원 절차와 자료가 필요하다. 점검의 성공을 운전 권한이나 장비 상태 증명으로 사용하지 않는다.
