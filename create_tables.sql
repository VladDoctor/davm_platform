CREATE TABLE hugging_face_models(
    modelId            text               NOT NULL,
    sha                text               ,
    lastModified       text               ,
    tags               text[]             NOT NULL,
    pipeline_tag       text               NOT NULL,
    siblings           text[]             NOT NULL,
    private            boolean            NOT NULL,
    author             text               NOT NULL,
    config             text               ,
    securityStatus     text               ,
    _id                text               NOT NULL,
    id                 text               NOT NULL,
    datasets           text[]             NOT NULL,
    has_space          boolean            NOT NULL,
    domain             text               NOT NULL,
    slice_datetime     timestamp          default NULL,
    PRIMARY KEY(modelId)
);

CREATE TABLE hugging_face_models_daily_dynamics(
    id                 SERIAL,
    modelId            text               NOT NULL,
    likes              integer            NOT NULL,
    downloads          integer            NOT NULL,
    slice_datetime     timestamp          default NULL,
    PRIMARY KEY(id),
    CONSTRAINT fk_modelId FOREIGN KEY(modelId) REFERENCES hugging_face_models(modelId)
);

CREATE TABLE hugging_face_datasets(
    datasetId          text               NOT NULL,
    sha                text               NOT NULL,
    lastModified       text               NOT NULL,
    tags               text[]             NOT NULL,
    private            boolean            NOT NULL,
    author             text,
    description        text,
    citation           text,
    cardData           text,
    siblings           text[]             NOT NULL,
    _id                text               NOT NULL,
    disabled           text               NOT NULL,
    gated              text               NOT NULL,
    paperswithcode_id  text,
    tasks              text[]             NOT NULL,
    size               text[]             NOT NULL,
    slice_datetime     timestamp          default NULL,
    PRIMARY KEY(datasetId)
);

CREATE TABLE hugging_face_datasets_daily_dynamics(
    id                 SERIAL,
    datasetId          text               NOT NULL,
    likes              integer            NOT NULL,
    downloads          integer            NOT NULL,
    slice_datetime     timestamp          default NULL,
    PRIMARY KEY(id),
    CONSTRAINT fk_datasetId FOREIGN KEY(datasetId) REFERENCES hugging_face_datasets(datasetId)
);
