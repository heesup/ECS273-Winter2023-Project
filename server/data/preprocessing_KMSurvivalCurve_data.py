import os
import pandas as pd

from lifelines import KaplanMeierFitter
from humanize import naturalsize

import pyspark
import pyspark.sql.functions as F
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession


def KM_survival_curve_process():
    # To load Backblaze HDD dataset CSV files 
    print('[INFO] CSV file load starts')
    os.listdir('data')

    # Apache Spark initilization
    sc = SparkContext('local')
    spark = SparkSession(sc)

    # Read Backblaze Data sets(period: 2020.1.1 ~ 2022.12.31)
    df = spark.read.csv('data', header=True)

    print('[INFO] CSV file load complete')
    # Data cleaning ===========================================================================
    dff = df.select(
            F.col("date").astype("date"),
            F.trim(F.col("serial_number")).alias("serial_number").astype("string"),
            F.trim(F.col("model")).alias("model").astype("string"),
            F.col("capacity_bytes").astype("bigint"),
            F.col("failure").astype("int"),
            F.col("smart_9_raw").astype("bigint"),  # Smart 9: Power-On Hours (POH)
        )

    dfm = dff.withColumn(
            "manufacturer",
            F.when(F.col("model").like("ST%"), "Seagate")
            .when(F.col("model").like("Hitachi %"), "Hitachi")
            .when(F.col("model").like("HGST %"), "Hitachi")
            .when(F.col("model").like("WD%"), "WDC")
            .when(F.col("model").like("%CT%"), "Micron")
            .when(F.col("model").like("%MT%"), "Micron")
            .when(F.col("model").like("% %"), F.split(F.col("model"), " ")[0])
            .otherwise("unknown"),
        )

    # Data aggregation ===========================================================================
    dfm.createOrReplaceTempView('drive_days')

    drive_spans = spark.sql("""
                                select
                                    manufacturer,
                                    model,
                                    serial_number,
                                    max(date) as retired_date,
                                    min(date) as launched_date,
                                    count(date) as observed_days,
                                    max(capacity_bytes) as capacity_bytes,
                                    min(case when failure=1 then date end) as failed_date,
                                    max(smart_9_raw) as max_hours,
                                    min(case when failure=1 then smart_9_raw end) as failed_hours,
                                    max(failure) as failure
                                from drive_days
                                group by manufacturer, model, serial_number
                            """).cache()

    print('[INFO] HardDiskDrive spans count: ', drive_spans.count())

    # drive_spans.write.mode('overwrite').parquet('drive_spans')
    drive_spans.createOrReplaceTempView('drive_spans')

    # Data for HDDs Survival ===========================================================================
    dfsurv = spark.sql("""
                        select
                            drive_spans.*,
                            datediff(coalesce(failed_date, retired_date), launched_date) as duration,
                            min(launched_date) over (partition by model) as model_introduced,
                            percentile_approx(capacity_bytes, 0.5) over (partition by model order by capacity_bytes) as model_capacity
                        from drive_spans
                        """)

    pdsurv = (
                dfsurv.select(
                    "serial_number",
                    "manufacturer",
                    "model",
                    "model_introduced",
                    "model_capacity",
                    "launched_date",
                    "duration",
                    "failure",
                )
                .toPandas()
                .assign(
                    launched_date=lambda x: pd.to_datetime(x.launched_date),
                    model_introduced=lambda x: pd.to_datetime(x.model_introduced),
                )
                .set_index("serial_number")
            )
    # Remove garbage data
    pdsurv = pdsurv.dropna(subset=['duration'])
    pdsurv.to_csv('./pdsurv_2020_2022.csv')


if __name__ == "__main__":
    KM_survival_curve_process()
