import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from scipy.signal import find_peaks, windows


EPSILON = 1e-12


def make_signal(amplitude, frequency, sample_rate, number_of_samples):
    """Create the sample numbers n and the sampled sine wave x[n]."""
    n = np.arange(number_of_samples)
    x = amplitude * np.sin(2 * np.pi * frequency * n / sample_rate)
    return n, x


def make_windows(window_length, number_of_samples):
    """Make short windows, then add zeros so every window has N samples."""
    short_windows = {
        "Rectangular": windows.boxcar(window_length),
        "Hann": windows.hann(window_length),
        "Hamming": windows.hamming(window_length),
    }

    full_windows = {}
    for name, short_window in short_windows.items():
        full_window = np.zeros(number_of_samples)
        full_window[:window_length] = short_window
        full_windows[name] = full_window

    return short_windows, full_windows


def fft_spectrum(signal, sample_rate, nfft):
    """Return the positive-frequency FFT magnitude and its dB version."""
    fft_values = np.fft.rfft(signal, n=nfft)
    frequencies = np.fft.rfftfreq(nfft, d=1 / sample_rate)
    magnitude = np.abs(fft_values)

    # Divide by the largest value so the tallest point is 0 dB.
    peak = max(np.max(magnitude), EPSILON)
    magnitude_db = 20 * np.log10(np.maximum(magnitude / peak, EPSILON))
    return frequencies, magnitude, magnitude_db


def measure_window(window, sample_rate):
    """Measure the main lobe and largest side lobe of one window."""
    length = len(window)
    nfft = 16384  # Lots of FFT points make the window spectrum smooth.
    if length > nfft:
        nfft = 2 ** int(np.ceil(np.log2(length)))

    # fftshift puts 0 Hz in the middle of the graph.
    response = np.abs(np.fft.fftshift(np.fft.fft(window, n=nfft)))
    frequencies = np.fft.fftshift(np.fft.fftfreq(nfft, d=1 / sample_rate))
    response = response / np.max(response)

    middle = nfft // 2
    right_half = response[middle:]

    # The first dip after the peak is our estimate of the first null.
    minimum_points, _ = find_peaks(-right_half)
    if len(minimum_points) == 0:
        first_null_index = np.argmin(right_half[1 : nfft // 4]) + 1
    else:
        first_null_index = minimum_points[0]

    first_null_hz = frequencies[middle + first_null_index]
    main_lobe_hz = 2 * first_null_hz
    main_lobe_bins = main_lobe_hz / (sample_rate / length)

    # Everything outside the two first nulls is treated as a side lobe.
    side_lobes = np.r_[response[: middle - first_null_index], response[middle + first_null_index + 1 :]]
    side_lobe_db = 20 * np.log10(max(np.max(side_lobes), EPSILON))
    response_db = 20 * np.log10(np.maximum(response, EPSILON))

    return frequencies, response_db, main_lobe_bins, main_lobe_hz, side_lobe_db


def add_labels(axis, x_label, y_label, title):
    """Use the same clear labels and grid on each plot."""
    axis.set_xlabel(x_label)
    axis.set_ylabel(y_label)
    axis.set_title(title)
    axis.grid(alpha=0.3)


def main():
    st.set_page_config(page_title="Spectral Leakage Analyzer", layout="wide")
    st.title("Windowing Effect on Spectral Leakage Analyzer")
    st.write("Change the inputs in the sidebar and watch the signals and spectra update.")

    # --- Sidebar inputs ---
    st.sidebar.header("Signal parameters")
    amplitude = st.sidebar.number_input("Amplitude A", min_value=0.0, value=1.0, step=0.1)
    frequency = st.sidebar.number_input("Sine frequency f0 (Hz)", min_value=0.0, value=123.5, step=1.0)
    sample_rate = st.sidebar.number_input("Sample rate Fs (Hz)", min_value=1.0, value=1000.0, step=100.0)
    number_of_samples = int(st.sidebar.number_input("Number of samples N", min_value=2, value=128, step=1))

    st.sidebar.header("Window and FFT")
    window_length = int(
        st.sidebar.number_input("Window length L", min_value=2, max_value=number_of_samples, value=min(128, number_of_samples), step=1)
    )
    chosen_windows = st.sidebar.multiselect(
        "Windows to show", ["Rectangular", "Hann", "Hamming"], default=["Rectangular", "Hann", "Hamming"]
    )
    nfft = int(st.sidebar.number_input("Zero-padded FFT length", min_value=number_of_samples, value=max(1024, number_of_samples), step=1))

    if frequency >= sample_rate / 2:
        st.error("f0 must be below Fs/2 (the Nyquist frequency).")
        st.stop()
    if not chosen_windows:
        st.warning("Choose at least one window to see windowed signals and FFTs.")

    # --- Signal ---
    n, x = make_signal(amplitude, frequency, sample_rate, number_of_samples)
    time = np.linspace(0, (number_of_samples - 1) / sample_rate, 1000)
    continuous_x = amplitude * np.sin(2 * np.pi * frequency * time)

    st.header("1. Input signal")
    st.latex(rf"x[n] = {amplitude:g}\sin\left(2\pi\,{frequency:g}\,n/{sample_rate:g}\right)")
    figure, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(time, continuous_x, label="Continuous x(t)")
    axes[0].plot(n / sample_rate, x, "o", label="Samples x[n]")
    add_labels(axes[0], "Time (s)", "Amplitude", "Continuous signal and samples")
    axes[0].legend()

    axes[1].stem(n, x, basefmt=" ")
    add_labels(axes[1], "n", "Amplitude", "Discrete-time signal x[n]")
    figure.tight_layout()
    st.pyplot(figure, clear_figure=True)
    st.caption("The dots are samples of the smooth continuous-time sine wave. Here, t = n/Fs.")

    # --- Windows ---
    short_windows, full_windows = make_windows(window_length, number_of_samples)
    st.header("2. Window functions")
    figure, axis = plt.subplots(figsize=(10, 4))
    for name, window in short_windows.items():
        axis.plot(window, label=name, linewidth=2)
    add_labels(axis, "Window sample", "Window value", "Rectangular, Hann, and Hamming windows")
    axis.legend()
    figure.tight_layout()
    st.pyplot(figure, clear_figure=True)
    st.write("A rectangular window stops abruptly. Hann fades to zero at both ends. Hamming is tapered but does not quite reach zero.")

    # Multiply values at the same sample number: x_windowed[n] = x[n] * w[n].
    windowed_signals = {}
    for name in chosen_windows:
        windowed_signals[name] = x * full_windows[name]

    st.header("3. Windowed signals")
    st.latex(r"x_w[n] = x[n] \cdot w[n]")
    if windowed_signals:
        figure, axis = plt.subplots(figsize=(10, 4))
        for name, signal in windowed_signals.items():
            axis.plot(n, signal, label=name)
        add_labels(axis, "n", "Amplitude", "Signal after windowing")
        axis.legend()
        figure.tight_layout()
        st.pyplot(figure, clear_figure=True)
    st.caption("The * symbol means element-wise multiplication: sample 0 is multiplied by window value 0, sample 1 by window value 1, and so on.")

    # --- FFT plots ---
    if windowed_signals:
        st.header("4. FFT without zero padding")
        figure, axes = plt.subplots(1, 2, figsize=(12, 4))
        for name, signal in windowed_signals.items():
            frequencies, magnitude, magnitude_db = fft_spectrum(signal, sample_rate, number_of_samples)
            axes[0].plot(frequencies, magnitude, label=name)
            axes[1].plot(frequencies, magnitude_db, label=name)
        add_labels(axes[0], "Frequency (Hz)", "Magnitude", f"{number_of_samples}-point FFT")
        add_labels(axes[1], "Frequency (Hz)", "dB (peak = 0)", "Normalised dB spectrum")
        axes[1].set_ylim(-120, 5)
        for axis in axes:
            axis.legend()
        figure.tight_layout()
        st.pyplot(figure, clear_figure=True)
        st.caption("Each dB curve is scaled so its highest point is 0 dB. This makes the side lobes easy to compare.")

        st.header("5. FFT with zero padding")
        figure, axes = plt.subplots(1, 2, figsize=(12, 4))
        for name, signal in windowed_signals.items():
            frequencies, magnitude, magnitude_db = fft_spectrum(signal, sample_rate, nfft)
            axes[0].plot(frequencies, magnitude, label=name)
            axes[1].plot(frequencies, magnitude_db, label=name)
        add_labels(axes[0], "Frequency (Hz)", "Magnitude", f"{nfft}-point zero-padded FFT")
        add_labels(axes[1], "Frequency (Hz)", "dB (peak = 0)", "Normalised dB spectrum")
        axes[1].set_ylim(-120, 5)
        for axis in axes:
            axis.legend()
        figure.tight_layout()
        st.pyplot(figure, clear_figure=True)
        st.info("Zero padding does not add information or reduce leakage. It only gives more points on the same frequency-domain curve, making the peak easier to read.")

    # --- Window-only measurements ---
    st.header("6. Window characteristics")
    figure, axis = plt.subplots(figsize=(10, 4))
    table_rows = []
    for name, window in short_windows.items():
        frequencies, response_db, width_bins, width_hz, side_lobe_db = measure_window(window, sample_rate)
        axis.plot(frequencies, response_db, label=name)
        table_rows.append(
            {
                "Window": name,
                "Main lobe (bins)": round(width_bins, 2),
                "Main lobe (Hz)": round(width_hz, 2),
                "Largest side lobe (dB)": round(side_lobe_db, 2),
            }
        )
    add_labels(axis, "Frequency (Hz)", "dB (peak = 0)", "Window spectra")
    axis.set_ylim(-120, 5)
    axis.legend()
    figure.tight_layout()
    st.pyplot(figure, clear_figure=True)
    st.table(table_rows)
    st.caption("The first dip on each side of the centre peak estimates the main-lobe edge. The highest remaining point is the largest side lobe. These numbers describe the windows themselves, not the chosen sine frequency.")

    st.header("What this shows")
    st.write(
        "A finite recording acts like a window. Multiplying the signal by a window in time changes its spectrum: in frequency, multiplication becomes convolution. "
        "A narrow main lobe helps separate nearby tones, while low side lobes reduce leakage from a strong nearby tone. This is a trade-off, so no one window is always best."
    )


if __name__ == "__main__":
    main()