import pandera.pandas as pa

import os
from abc import ABC, abstractmethod

class BaseRawDataPipeline(ABC):
    def __init__(
        self,
        input_data_path: str | os.PathLike,
        output_data_path: str | os.PathLike
    ):
        self.input_data_path = input_data_path
        self.output_data_path = output_data_path

    @abstractmethod
    def transform(self, raw_data):
        """Transform the raw data.
        
        Args:
            raw_data: The raw data to be transformed.
        """

    @abstractmethod
    def load(self):
        """Load in the raw data."""

    # def save(self, transformed_data):
    #     """save the transformed data to parquet."""
    #     transformed_data.sink_parquet(
    #         self.output_file_path,
    #     )

    @property
    def output_schema(self):
        return pa.DataFrameSchema(
            {
                "Field": pa.Column(str),
                "Variety": pa.Column(str),
                "Year": pa.Column(int, pa.Check.ge(0)),
                "Hours Zupfen": pa.Column(float, nullable=True),
                "Hours Ernte": pa.Column(float, nullable=True)
            },
            index = pa.Index(int),
        )

    def validate(self, transformed_data):
        """validate the transformed data."""
        self.output_schema.validate(transformed_data)

    def run(self, **kwargs):
        """Run the data cleaning pipeline."""
        raw_data = self.load(**kwargs)
        output = self.transform(raw_data)
        self.validate(output)
        return output