from __future__ import annotations

from scripts.plot_ledger import prepare_plot_data


def test_prepare_plot_data_excludes_cap_violating_rounds_but_labels_them() -> None:
    records = [
        {
            "round": 1,
            "dataset": "small",
            "ler": 0.01,
            "decode_seconds": 4.0,
            "time_cap_seconds": 30.0,
            "status": "pass",
            "round_status": "pass",
            "round_score": 0.02,
        },
        {
            "round": 1,
            "dataset": "large",
            "ler": 0.02,
            "decode_seconds": 6.0,
            "time_cap_seconds": 30.0,
            "status": "pass",
            "round_status": "pass",
            "round_score": 0.02,
        },
        {
            "round": 2,
            "dataset": "small",
            "ler": 0.03,
            "decode_seconds": 35.0,
            "time_cap_seconds": 30.0,
            "status": "fail",
            "failure_reason": "decode_timeout",
            "round_status": "fail",
            "round_score": 1.0,
        },
        {
            "round": 2,
            "dataset": "large",
            "ler": 1.0,
            "decode_seconds": 45.0,
            "time_cap_seconds": 30.0,
            "status": "fail",
            "failure_reason": "decode_timeout",
            "round_status": "fail",
            "round_score": 1.0,
        },
    ]

    plot_data = prepare_plot_data(records)

    assert plot_data.plot_rounds == [1]
    assert plot_data.ler_points == [(1, 0.01, "small"), (1, 0.02, "large")]
    assert plot_data.decode_time_points == [(1, 4.0, "small"), (1, 6.0, "large")]
    assert plot_data.round_score_points == [(1, 0.02)]
    assert plot_data.excluded_rounds == [2]
    assert plot_data.excluded_labels == {2: "30s cap violated"}
