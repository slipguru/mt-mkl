import os
import numpy as np
import pandas as pd
from os.path import join
from mtmkl.signalprocessing.filter_artifacts import PreProcessing, remove_edges
from mtmkl.signalprocessing.wavelet_transform import CWTTransform
from mtmkl.signalprocessing.kernel_function import correlation, phaselockingvalue, fourier_corr


def main():
    path = "/home/vanessa/DATA_SEEG/PKL_FILE/"
    folderlist = [f for f in os.listdir(path) if not (f.endswith(".pkl") or f.startswith("_"))]
    print(folderlist)
    # sampling frequency for our acquisitions is equivalent to 1 kHz
    sampling_freq = 1000.
    pathkernel = ["plv", "corr", "cross"]

    for f in folderlist:
        print("patient", f)

        ff = pd.read_pickle(join(path, f, "data.pkl"))

        try:
            os.mkdir(join(path, f, "kernel"))
            for pathk in pathkernel:
                os.mkdir(join(path, f, "kernel", pathk))
        except:
            pass

        print(ff.keys())

        # the pickle is such that it contains in the last columns the structural features for the channel of acquisition
        # we want to see where we have the true values - the first string column corresponds to the y - medical tag for epileptic or not
        colsstr = np.where([isinstance(k, str) for k in ff.keys()])[0]
        # for the patients with structural features this corresponds to ["Y", "ptd", spatial coordinates] otherwise just the tag as provided by medical experts

        values = ff.values[:, :colsstr[0]]  # recordings for all channels

        PreProcess = PreProcessing(fs=sampling_freq)
        values = PreProcess.remove_powerline(values)

        WaveletTransf = CWTTransform(fs=sampling_freq)
        central_freqs = WaveletTransf.freqs

        for n in range(WaveletTransf.nscales):
            print("central frequency", str(central_freqs[n]))
            cwt_coefs = WaveletTransf.cwt(values, n)

            # we want to remove the edges, after all the filtering part
            cwt_coefs = remove_edges(cwt_coefs)

            ### for the entire time series
            pd.DataFrame(data=phaselockingvalue(cwt_coefs), index=ff.index,
                        columns=ff.index).to_csv(join(path, f, "kernel", pathkernel[0], "scale_"+str(n)+".csv"))

            pd.DataFrame(data=correlation(np.abs(cwt_coefs)), index=ff.index,  columns=ff.index).to_csv(join(path, f, "kernel", pathkernel[1], "scale_"+str(n)+".csv"))

            pd.DataFrame(data=fourier_corr(cwt_coefs), index=ff.index, columns=ff.index).to_csv(join(path, f, "kernel", pathkernel[2], "scale_"+str(n)+".csv"))



if __name__ == '__main__':
    main()
