import numpy as np

from pydantic import ConfigDict, BaseModel as PydanticBase, Field, model_validator

from app.database.models.stackups import Stackup

class AnalysisParamsModel(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    start_freq: int = Field(default=0,gt=0)
    stop_freq: int = Field(default=18e9,gt=0)
    points_per_mhz: int = Field(default=1, gt=0)
    rbw: int = Field(default=1e6,gt=0)
    temp: int
    pwr_in: int
    min_snr: int

    @model_validator(mode="after")
    def validate_freq_range(self):
        if self.start_freq >= self.stop_freq:
            raise ValueError("start_freq must be less than stop_freq.")
        return self
    
class CascadeResultsModel(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    freq: list[list[int]] | None = None
    gain: list[list[int]] | None = None
    nf: list[list[int]] | None = None
    p1db: list[list[int]] | None = None

def analyze(stackup: list[Stackup], params: AnalysisParamsModel) -> CascadeResultsModel:
    """Perform a cascade analysis of an RF stackup"""
    results = CascadeResultsModel()
    freq_mat = analysis_freqs(stackup,params)
    gain = cascade_gain(stackup, freq_mat)
    nf = cascade_nf(stackup,gain,freq_mat)

    results.freq = freq_mat.tolist()
    results.gain = gain.tolist()
    results.nf = nf.tolist()
    return results

def analysis_freqs(stackup: list[Stackup], params: AnalysisParamsModel) -> np.ndarray[int]:
    num_points = int((params.stop_freq-params.start_freq)/(1e6*params.points_per_mhz))+1
    freqs = np.linspace(params.start_freq,params.stop_freq,num_points,dtype=int)
    freq_mat = np.tile(freqs, (len(stackup), 1))
    return freq_mat

def cascade_gain(stackup: list[Stackup], freq_mat: np.ndarray[int]) -> np.ndarray[float]:
    gain = np.full(freq_mat.shape(),None)
    for i,comp in enumerate(stackup):
        new_gain = np.interp(freq_mat[i],comp.component_version.component_data.gain["freq"], comp.component_version.component_data.gain["mag"])
        if i == 0:
            gain[i] = new_gain
        else:
            gain[i] = gain[i-1] + new_gain
    return gain

def cascade_nf(stackup: list[Stackup], gain: np.ndarray[float], freq_mat: np.ndarray[int]) -> np.ndarray[float]:
    nf = np.full(freq_mat.shape(),None)
    for i,comp in enumerate(stackup):
        new_nf = np.interp(freq_mat[i],comp.component_version.component_data.nf["freq"], comp.component_version.component_data.nf["mag"])
        if i == 0:
            nf[i] = new_nf
        else:
            prev_lin_nf = 10**(nf[i-1]/10)
            cur_lin_nf = 10**(new_nf/10)
            casc_lin_gain = 10**(gain[i]/10)
            nf[i] = 10*np.log10(prev_lin_nf + (cur_lin_nf - 1)/casc_lin_gain)
    return nf