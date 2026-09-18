# """Interactive visual guide to windowing and spectral leakage.

# Run with: streamlit run app.py
# """

# import matplotlib.pyplot as plt
# import numpy as np
# import streamlit as st
# from scipy.signal import find_peaks
# from scipy.signal import windows


# WINDOW_BUILDERS = {
#     "Rectangular": windows.boxcar,
#     "Hann": windows.hann,
#     "Hamming": windows.hamming,
# }
# EPSILON = 1e-12

# """Returnx[n] = A sin(2 pi f0 n / Fs)."""
# def generate_discrete_signal(amplitude, frequency, sample_rate, samples):
#     n = np.arange(samples)
#     x = amplitude * np.sin(2 * np.pi * frequency * n / sample_rate)
#     return n, x


# def generate_continuous_signal(amplitude, frequency, sample_rate, samples):
#     """Make a dense curve over the same time interval as the samples."""
#     t = np.linspace(0, (samples - 1) / sample_rate, 1000)
#     x_continuous = amplitude * np.sin(2 * np.pi * frequency * t)
#     return t, x_continuous


# def generate_windows(length):
#     """Create the three length-L SciPy windows used in this demonstration."""
#     return {name: builder(length, sym=True) for name, builder in WINDOW_BUILDERS.items()}


# def make_full_length_window(short_window, samples):
    
#     full_window = np.zeros(samples)
#     full_window[: len(short_window)] = short_window
#     return full_window


# def apply_window(signal, full_window):
#     return signal * full_window


# def compute_spectrum(signal, sample_rate, nfft=None):
#     """Return the one-sided FFT magnitude and a peak-normalised dB version."""
#     if nfft is None:
#         nfft = len(signal)

#     fft_values = np.fft.rfft(signal, n=nfft)
#     frequencies = np.fft.rfftfreq(nfft, d=1 / sample_rate)
#     magnitude = np.abs(fft_values)
#     peak = max(float(np.max(magnitude)), EPSILON)
#     magnitude_db = 20 * np.log10(np.maximum(magnitude, EPSILON) / peak)
#     return frequencies, magnitude, magnitude_db


# def _first_null_offset(half_magnitude):
#     """Find the first local minimum to the right of a window spectrum's centre.

#     A finite FFT samples a theoretical null imperfectly, especially for a Hamming
#     window.  The first local minimum is therefore a practical, reproducible
#     estimate of the first null.
#     """
#     minima, _ = find_peaks(-half_magnitude)
#     if len(minima):
#         return int(minima[0])

#     # This fallback keeps the metric useful even if the FFT grid has no sampled
#     # local minimum. It chooses the lowest point in the first quarter-spectrum.
#     search_end = max(2, len(half_magnitude) // 4)
#     return int(np.argmin(half_magnitude[1:search_end]) + 1)


# def calculate_window_metrics(window, sample_rate):
#     """Measure a window's main lobe and largest side lobe from its own FFT."""
#     length = len(window)
#     # A dense, power-of-two FFT makes null and side-lobe locations easy to see.
#     nfft = max(16384, 1 << int(np.ceil(np.log2(length * 64))))
#     response = np.fft.fftshift(np.fft.fft(window, n=nfft))
#     frequency = np.fft.fftshift(np.fft.fftfreq(nfft, d=1 / sample_rate))
#     magnitude = np.abs(response)
#     magnitude /= max(float(np.max(magnitude)), EPSILON)

#     centre = nfft // 2
#     offset = _first_null_offset(magnitude[centre:])
#     null_frequency = abs(frequency[centre + offset])
#     main_lobe_hz = 2 * null_frequency
#     main_lobe_bins = main_lobe_hz / (sample_rate / length)

#     # Points outside the two first minima form the side-lobe region.
#     side_lobes = np.concatenate((magnitude[: centre - offset], magnitude[centre + offset + 1 :]))
#     side_lobe_level_db = 20 * np.log10(max(float(np.max(side_lobes)), EPSILON))

#     return {
#         "frequency": frequency,
#         "magnitude_db": 20 * np.log10(np.maximum(magnitude, EPSILON)),
#         "first_null_hz": null_frequency,
#         "main_lobe_bins": main_lobe_bins,
#         "main_lobe_hz": main_lobe_hz,
#         "side_lobe_db": side_lobe_level_db,
#     }


# def _style_axis(axis, xlabel, ylabel, title):
#     axis.set_xlabel(xlabel)
#     axis.set_ylabel(ylabel)
#     axis.set_title(title)
#     axis.grid(True, alpha=0.3)


# def plot_input_signal(n, x, t, x_continuous, sample_rate):
#     """Plot continuous and sampled versions side by side."""
#     figure, axes = plt.subplots(1, 2, figsize=(12, 4))
#     axes[0].plot(t, x_continuous, color="#2463a7", label="Continuous x(t)")
#     axes[0].plot(n / sample_rate, x, "o", color="#e07020", ms=4, label="Samples x[n]")
#     _style_axis(axes[0], "Time (s)", "Amplitude", "Continuous representation and samples")
#     axes[0].legend()

#     markerline, stemlines, baseline = axes[1].stem(n, x, basefmt=" ")
#     plt.setp(markerline, markersize=4, color="#e07020")
#     plt.setp(stemlines, color="#e07020")
#     _style_axis(axes[1], "n", "Amplitude", "Discrete-time signal x[n]")
#     figure.tight_layout()
#     return figure


# def plot_windows(short_windows):
#     figure, axis = plt.subplots(figsize=(10, 4))
#     for name, window in short_windows.items():
#         axis.plot(np.arange(len(window)), window, label=name, linewidth=2)
#     _style_axis(axis, "Window sample", "Window value", "Window functions")
#     axis.legend()
#     figure.tight_layout()
#     return figure


# def plot_windowed_signals(n, windowed_signals):
#     figure, axis = plt.subplots(figsize=(10, 4))
#     for name, signal in windowed_signals.items():
#         axis.plot(n, signal, label=f"x[n] x {name}", linewidth=1.7)
#     _style_axis(axis, "n", "Amplitude", "Windowed signals")
#     axis.legend()
#     figure.tight_layout()
#     return figure


# def plot_spectra(spectra, title_prefix):
#     figure, axes = plt.subplots(1, 2, figsize=(12, 4))
#     for name, (frequency, magnitude, magnitude_db) in spectra.items():
#         axes[0].plot(frequency, magnitude, label=name)
#         axes[1].plot(frequency, magnitude_db, label=name)
#     _style_axis(axes[0], "Frequency (Hz)", "Magnitude", f"{title_prefix}: magnitude")
#     _style_axis(axes[1], "Frequency (Hz)", "Magnitude (dB, peak = 0)", f"{title_prefix}: dB")
#     axes[1].set_ylim(-120, 5)
#     for axis in axes:
#         axis.legend()
#     figure.tight_layout()
#     return figure


# def plot_window_responses(metrics):
#     figure, axis = plt.subplots(figsize=(10, 4))
#     for name, values in metrics.items():
#         axis.plot(values["frequency"], values["magnitude_db"], label=name)
#     _style_axis(axis, "Frequency (Hz)", "Magnitude (dB, peak = 0)", "High-resolution window spectra")
#     axis.set_ylim(-120, 5)
#     axis.legend()
#     figure.tight_layout()
#     return figure


# def read_sidebar():
#     """Collect input controls. Streamlit reruns the script whenever one changes."""
#     st.sidebar.header("Signal parameters")
#     amplitude = st.sidebar.number_input("Amplitude A", min_value=0.0, value=1.0, step=0.1)
#     sample_rate = st.sidebar.number_input("Sampling frequency Fs (Hz)", min_value=0.1, value=1000.0, step=100.0)
#     frequency = st.sidebar.number_input("Sinusoidal frequency f0 (Hz)", min_value=0.0, value=123.5, step=1.0)
#     samples = int(st.sidebar.number_input("Number of samples N", min_value=2, value=128, step=1))

#     st.sidebar.header("Window parameters")
#     length = int(st.sidebar.number_input("Window length L", min_value=2, max_value=samples, value=min(128, samples), step=1))
#     selected = st.sidebar.multiselect("Windows to compare", list(WINDOW_BUILDERS), default=list(WINDOW_BUILDERS))

#     st.sidebar.header("FFT parameters")
#     default_nfft = max(1024, samples)
#     nfft = int(st.sidebar.number_input("Zero-padded FFT length NFFT", min_value=samples, value=default_nfft, step=1))
#     return amplitude, frequency, sample_rate, samples, length, selected, nfft


# def main():
#     st.set_page_config(page_title="Spectral Leakage Analyzer", layout="wide")
#     st.title("Windowing Effect on Spectral Leakage Analyzer")
#     st.write("An interactive DSP visualisation of sampling, finite records, windowing, and FFT spectra.")

#     amplitude, frequency, sample_rate, samples, length, selected, nfft = read_sidebar()
#     if frequency >= sample_rate / 2:
#         st.error("Choose f0 below Fs/2 (the Nyquist frequency) to avoid aliasing.")
#         st.stop()
#     if not selected:
#         st.warning("Select at least one window to display the windowed signals and spectra.")

#     n, x = generate_discrete_signal(amplitude, frequency, sample_rate, samples)
#     t, x_continuous = generate_continuous_signal(amplitude, frequency, sample_rate, samples)
#     short_windows = generate_windows(length)
#     full_windows = {name: make_full_length_window(window, samples) for name, window in short_windows.items()}
#     windowed = {name: apply_window(x, full_windows[name]) for name in selected}

#     st.header("1. Input signal")
#     st.latex(rf"x[n] = {amplitude:g}\sin\left(2\pi\,{frequency:g}\,n / {sample_rate:g}\right), \qquad t=n/F_s")
#     st.pyplot(plot_input_signal(n, x, t, x_continuous, sample_rate), clear_figure=True)
#     st.caption("The smooth curve is x(t); dots and stems show the samples x[n] = x(n/Fs).")

#     st.header("2. Window functions")
#     st.pyplot(plot_windows(short_windows), clear_figure=True)
#     st.markdown(
#         "- Rectangular: $w[n]=1$ (an abrupt start and end).\n"
#         "- Hann: $w[n]=0.5-0.5\\cos(2\\pi n/(L-1))$ (reaches zero at both ends).\n"
#         "- Hamming: $w[n]=0.54-0.46\\cos(2\\pi n/(L-1))$ (tapered, but its endpoints are not zero)."
#     )

#     st.header("3. Windowed signals")
#     st.latex(r"x_w[n] = x[n],w[n]")
#     if windowed:
#         st.pyplot(plot_windowed_signals(n, windowed), clear_figure=True)
#     st.caption("The arrays x[n] and w[n] both have N values. The * operator multiplies corresponding values element by element.")

#     if windowed:
#         no_padding = {name: compute_spectrum(signal, sample_rate) for name, signal in windowed.items()}
#         st.header("4. DFT without zero padding")
#         st.pyplot(plot_spectra(no_padding, f"{samples}-point FFT"), clear_figure=True)
#         st.caption("The dB curves are normalised so each spectrum's largest value is 0 dB. This makes leakage patterns comparable even when windows have different peak gains.")

#         zero_padded = {name: compute_spectrum(signal, sample_rate, nfft) for name, signal in windowed.items()}
#         st.header("5. DFT with zero padding")
#         st.pyplot(plot_spectra(zero_padded, f"{nfft}-point zero-padded FFT"), clear_figure=True)
#         st.info("Zero padding adds no signal information, does not reduce leakage, and does not change the fundamental resolution set by the observation length. It samples the same spectrum more densely, so peaks are easier to inspect.")

#     st.header("6. Window characteristics")
#     metrics = {name: calculate_window_metrics(window, sample_rate) for name, window in short_windows.items()}
#     st.pyplot(plot_window_responses(metrics), clear_figure=True)
#     rows = [
#         {
#             "Window": name,
#             "Main-lobe width (bins)": round(values["main_lobe_bins"], 3),
#             "Main-lobe width (Hz)": round(values["main_lobe_hz"], 3),
#             "Maximum side-lobe (dB)": round(values["side_lobe_db"], 2),
#         }
#         for name, values in metrics.items()
#     ]
#     st.table(rows)
#     st.caption("First nulls are estimated as the first local magnitude minimum on either side of the centred, high-resolution window FFT. The side-lobe level is the largest point outside those two minima. These are properties of the length-L windows, not of f0.")

#     st.header("7. Interpretation")
#     st.markdown(
#         "A continuous sinusoid is sampled, observed for only N points, multiplied by a window, and transformed with an FFT. "
#         "Time-domain multiplication corresponds to frequency-domain convolution, so the window spectrum shapes the sinusoid's spectral leakage. "
#         "A narrower main lobe helps separate close frequencies; lower side lobes better suppress leakage from a strong nearby tone. No window is universally best - it is a trade-off."
#     )


# if __name__ == "__main__":
#      main()