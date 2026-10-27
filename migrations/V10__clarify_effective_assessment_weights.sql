-- MF=((AV1+AV2)/2+AV3)/2 is equivalent to (AV1+AV2+2*AV3)/4.
-- This metadata does not introduce credit/workload weights into PMG.
UPDATE assessment_models
SET av3_has_greater_weight=TRUE,
    formula_description='Protótipo: MI=(AV1+AV2)/2 >=4; AV3 obrigatória >=4; MF=(MI+AV3)/2 >=5. Equivale a (AV1+AV2+2*AV3)/4; frequência mínima exigida.'
WHERE model_type='AV_SERIES';
