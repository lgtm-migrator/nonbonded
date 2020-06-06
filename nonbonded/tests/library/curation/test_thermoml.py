import os
import tarfile
from tempfile import NamedTemporaryFile

import pandas

from nonbonded.library.curation.components.thermoml import (
    ImportThermoMLData,
    ImportThermoMLDataSchema,
)
from nonbonded.library.utilities import get_data_filename


def test_import_thermoml_data(requests_mock):
    """Tests that ThermoML archive files can be imported from a
    remote source."""

    try:
        from pytest_cov.embed import cleanup_on_sigterm
    except ImportError:
        pass
    else:
        cleanup_on_sigterm()

    # Create a tarball to be downloaded.
    source_path = get_data_filename(os.path.join("tests", "thermoml", "density.xml"))

    with NamedTemporaryFile(suffix="tgz") as tar_file:

        with tarfile.open(tar_file.name, "w:gz") as tar:
            tar.add(source_path, arcname=os.path.basename(source_path))

        with open(tar_file.name, "rb") as file:

            requests_mock.get(
                "https://trc.nist.gov/ThermoML/IJT.tgz", content=file.read()
            )

        data_frame = ImportThermoMLData.apply(
            pandas.DataFrame(), ImportThermoMLDataSchema(journal_names=["IJT"])
        )

        assert data_frame is not None and len(data_frame) == 1
