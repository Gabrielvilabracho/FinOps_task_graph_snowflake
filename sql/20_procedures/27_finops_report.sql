USE DATABASE FINOPS_DEV;
USE SCHEMA FINOPS;

CREATE OR REPLACE PROCEDURE SP_FINOPS_BUILD_REPORT(P_RUN_ID STRING)
RETURNS OBJECT
LANGUAGE SQL
EXECUTE AS OWNER
AS
$$
DECLARE
  V_ANALYSIS_DATE DATE;
  V_ATTENTION_COUNT NUMBER;
  V_FAILED_COUNT NUMBER;
  V_INCOMPLETE_COUNT NUMBER;
  V_RULE_GAP_COUNT NUMBER;
  V_HIGHEST_MODULE_STATUS STRING;
  V_OVERALL_STATUS STRING;
  V_MODULE_SUMMARY OBJECT;
  V_MODULE_LINES STRING;
  V_REPORT_TEXT STRING;
  V_EVIDENCE_CONTRACT OBJECT;
BEGIN
  V_EVIDENCE_CONTRACT := OBJECT_CONSTRUCT(
    'version', 1,
    'scope_note', 'Do not sum overlapping consumption, billing and service-detail representations.',
    'pending_gates', ARRAY_CONSTRUCT(
      'Invoice/currency reconciliation and effective financial basis',
      'Effective-dated business ownership and shared-cost policy',
      'Non-cost anomaly rules and operational authorization',
      'Mature history for forecasting and realized savings'
    ),
    'actions_authorized', FALSE
  );
  SELECT ANALYSIS_DATE INTO :V_ANALYSIS_DATE
  FROM FINOPS_RUN
  WHERE RUN_ID = :P_RUN_ID;

  SELECT
    COUNT_IF(STATUS = 'ATTENTION'),
    COUNT_IF(STATUS = 'FAILED'),
    COUNT_IF(STATUS = 'DATA_INCOMPLETE'),
    COUNT_IF(STATUS IN ('RULE_NOT_CONFIGURED', 'REVIEW_REQUIRED')),
    OBJECT_AGG(
      MODULE_NAME,
      OBJECT_CONSTRUCT_KEEP_NULL(
        'status', STATUS,
        'metrics', METRICS,
        'finding_count', FINDING_COUNT,
        'error_code', ERROR_CODE,
        'error_message', ERROR_MESSAGE,
        'started_at', STARTED_AT,
        'completed_at', COMPLETED_AT
      )
    ),
    LISTAGG(MODULE_NAME || ': ' || STATUS
      || IFF(METRICS:evidence IS NULL, '',
        ' | basis=' || COALESCE(METRICS:evidence:basis::STRING, 'UNKNOWN')
        || ' | readiness=' || COALESCE(METRICS:evidence:reason::STRING, 'OBSERVED')
        || ' | baseline=' || COALESCE(METRICS:evidence:previous_reason::STRING, 'N/A_OR_OBSERVED')
        || ' | billed=' || COALESCE(METRICS:evidence:financial:reason::STRING, 'N/A_OR_OBSERVED')
        || ' | AI subset=' || COALESCE(METRICS:evidence:user_ai_reason::STRING, 'N/A_OR_OBSERVED')
        || ' | ' || COALESCE(METRICS:evidence:scope_note::STRING, '')),
      CHAR(10))
      WITHIN GROUP (ORDER BY MODULE_NAME)
  INTO
    :V_ATTENTION_COUNT,
    :V_FAILED_COUNT,
    :V_INCOMPLETE_COUNT,
    :V_RULE_GAP_COUNT,
    :V_MODULE_SUMMARY,
    :V_MODULE_LINES
  FROM FINOPS_MODULE_RUN
  WHERE RUN_ID = :P_RUN_ID;

  SELECT STATUS INTO :V_HIGHEST_MODULE_STATUS
  FROM FINOPS_MODULE_RUN
  WHERE RUN_ID = :P_RUN_ID
  ORDER BY FINOPS_STATUS_PRECEDENCE(STATUS) DESC, MODULE_NAME
  LIMIT 1;

  V_OVERALL_STATUS := CASE V_HIGHEST_MODULE_STATUS
    WHEN 'FAILED' THEN 'FAILED'
    WHEN 'DATA_INCOMPLETE' THEN 'DATA_INCOMPLETE'
    WHEN 'ATTENTION' THEN 'ATTENTION_REQUIRED'
    WHEN 'ATTENTION_REQUIRED' THEN 'ATTENTION_REQUIRED'
    WHEN 'RULE_NOT_CONFIGURED' THEN 'REVIEW_REQUIRED'
    WHEN 'REVIEW_REQUIRED' THEN 'REVIEW_REQUIRED'
    ELSE 'NORMAL'
  END;

  V_REPORT_TEXT :=
    'Analysis date: ' || V_ANALYSIS_DATE::STRING || CHAR(10)
    || COALESCE(V_MODULE_LINES, 'No module results were recorded.') || CHAR(10)
    || 'Overall: ' || V_OVERALL_STATUS || CHAR(10)
    || 'Do not sum overlapping credit representations. Residual is not proven waste.' || CHAR(10)
    || 'Pending gates: invoice/currency, ownership/allocation, policy approval, mature history.' || CHAR(10)
    || 'No automatic remediation is authorized by this report.';

  MERGE INTO FINOPS_DAILY_REPORT target
  USING (
    SELECT
      :P_RUN_ID AS RUN_ID,
      :V_ANALYSIS_DATE AS ANALYSIS_DATE,
      :V_OVERALL_STATUS AS OVERALL_STATUS,
      OBJECT_CONSTRUCT(
        'modules', :V_MODULE_SUMMARY,
        'attention_count', :V_ATTENTION_COUNT,
        'failed_count', :V_FAILED_COUNT,
        'incomplete_count', :V_INCOMPLETE_COUNT,
        'rule_gap_count', :V_RULE_GAP_COUNT,
        'evidence_contract', :V_EVIDENCE_CONTRACT
      ) AS SUMMARY,
      :V_REPORT_TEXT AS REPORT_TEXT
  ) source
  ON target.RUN_ID = source.RUN_ID
  WHEN MATCHED THEN UPDATE SET
    target.ANALYSIS_DATE = source.ANALYSIS_DATE,
    target.OVERALL_STATUS = source.OVERALL_STATUS,
    target.SUMMARY = source.SUMMARY,
    target.REPORT_TEXT = source.REPORT_TEXT,
    target.GENERATED_AT = CURRENT_TIMESTAMP()
  WHEN NOT MATCHED THEN INSERT (
    RUN_ID, ANALYSIS_DATE, OVERALL_STATUS, SUMMARY, REPORT_TEXT
  ) VALUES (
    source.RUN_ID, source.ANALYSIS_DATE, source.OVERALL_STATUS,
    source.SUMMARY, source.REPORT_TEXT
  );

  UPDATE FINOPS_RUN
  SET
    STATUS = :V_OVERALL_STATUS,
    ATTENTION_COUNT = :V_ATTENTION_COUNT,
    FAILED_COUNT = :V_FAILED_COUNT,
    RULE_GAP_COUNT = :V_RULE_GAP_COUNT,
    COMPLETED_AT = IFF(:V_OVERALL_STATUS = 'RUNNING', NULL, CURRENT_TIMESTAMP()),
    UPDATED_AT = CURRENT_TIMESTAMP()
  WHERE RUN_ID = :P_RUN_ID;

  RETURN OBJECT_CONSTRUCT(
    'run_id', P_RUN_ID,
    'analysis_date', V_ANALYSIS_DATE,
    'overall_status', V_OVERALL_STATUS,
    'summary', V_MODULE_SUMMARY,
    'evidence_contract', V_EVIDENCE_CONTRACT,
    'report_text', V_REPORT_TEXT
  );
END;
$$;
