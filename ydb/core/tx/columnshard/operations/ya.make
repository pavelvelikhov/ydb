LIBRARY()

SRCS(
    write.cpp
    write_data.cpp
    manager.cpp
    events.cpp
)

PEERDIR(
    ydb/core/protos
    ydb/core/tx/data_events
    ydb/services/metadata
    ydb/core/tx/columnshard/data_sharing/destination/events
    ydb/core/tx/columnshard/data_reader
    ydb/core/tx/columnshard/transactions/locks
    ydb/core/tx/columnshard/operations/batch_builder
    ydb/core/tx/columnshard/operations/slice_builder
    ydb/core/tx/columnshard/operations/common
)

END()
