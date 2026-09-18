# Windowing Effect on Spectral Leakage Analyzer

An interactive DSP visualization tool for understanding **spectral leakage** and the effect of different window functions on a finite-length sinusoidal signal.

The project allows the user to generate a discrete-time sinusoidal signal, apply different window functions, calculate its FFT, and compare the resulting frequency spectra.

## Project Overview

When a finite-length signal is analysed in the frequency domain, spectral leakage can occur because the finite record may introduce discontinuities when it is treated as a periodic sequence.

This project demonstrates how different window functions affect this behaviour.

The application compares:

- Rectangular Window
- Hann Window
- Hamming Window

The effect of each window is observed using:

- Time-domain signal representation
- Window functions
- Windowed signals
- FFT magnitude spectrum
- Normalized dB spectrum
- Main-lobe width
- Side-lobe level

## Features

### Signal Generation

The user can enter:

- Amplitude `A`
- Signal frequency `f0`
- Sampling frequency `Fs`
- Number of samples `N`

The application generates the discrete-time sinusoid:

\[
x[n] = A\sin\left(\frac{2\pi f_0 n}{F_s}\right)
\]

### Windowing

The following windows can be selected and compared:

- Rectangular
- Hann
- Hamming

The windowed signal is calculated using:

\[
x_w[n] = x[n]w[n]
\]

### FFT Analysis

The application calculates the frequency spectrum of the windowed signal using the Fast Fourier Transform (FFT).

Both:

- FFT without zero-padding
- Zero-padded FFT

are displayed for comparison.

### Magnitude and dB Spectrum

The magnitude spectrum is calculated from the FFT output.

The normalized dB spectrum is calculated using:

\[
X_{dB}[k] =
20\log_{10}
\left(
\frac{|X[k]|}{\max |X[k]|}
\right)
\]

This makes it easier to compare the side-lobe levels of different windows.

### Zero Padding

Zero-padding is included to provide a denser representation of the frequency spectrum.

Zero-padding:

- does not add new signal information
- does not improve the actual frequency resolution
- provides more closely spaced frequency samples
- makes the spectral shape easier to inspect

### Window Characteristics

The application also estimates:

- Main-lobe width in Hz
- Main-lobe width in bins
- Maximum side-lobe level in dB

These values are presented for each selected window.

## Application Flow

```text
User Inputs
     ↓
Generate Discrete-Time Signal
     ↓
Generate Window Functions
     ↓
Apply Window
xw[n] = x[n]w[n]
     ↓
   ┌───────────────┐
   │               │
   ↓               ↓
N-point FFT    Zero-Padded FFT
   │               │
   ↓               ↓
Magnitude + dB Spectrum
   │               │
   └───────┬───────┘
           ↓
   Compare Window Effects
           ↓
Main-Lobe Width + Side-Lobe Level
