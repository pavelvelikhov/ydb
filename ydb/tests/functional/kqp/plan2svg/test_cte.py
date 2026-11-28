import yatest.common


class TestCte:
    def test_toplevel(self, tmp_path):
        # Timeline rendering currently expects the legacy multi-statement plan.
        with open(yatest.common.source_path("ydb/tests/tools/kqprun/configuration/app_config.conf")) as source:
            config = source.read()
        config = config.replace("TableServiceConfig {", """TableServiceConfig {
  EnableFallbackOnMultipleStatements: true
  EnableFallbackToYqlOptimizer: true""", 1)
        config_path = tmp_path / "app_config.conf"
        config_path.write_text(config)
        yatest.common.execute(
            [
                yatest.common.binary_path("ydb/tests/tools/kqprun/kqprun"),
                "-c",
                str(config_path),
                "--sql",
                "SELECT 1; SELECT 1;",
                "--script-timeline-file",
                "timeline.svg",
            ]
        )
