from __future__ import division, print_function
import numpy as np
import scipy.signal as scisig

""" a number of mathematical convenience functions"""

def cabssquared(x):
    """Calculate the absolute squared of a complex number"""
    return x.real**2 + x.imag**2

def ttanh(x, A, x0, w):
    """
    Calculate the hyperbolic tangent with a given amplitude, zero offset and
    width.

    Parameters
    ----------
    x : array_like
        Input array variable
    A : float
        Amplitude
    x0 : float
        Zero-offset
    w : float
        Width

    Returns
    -------
    array_like
        calculated array
    """
    return A*tanh((x-x0)/w)

def gauss(x, A, x0, w):
    """
    Calculate the Gaussian function with a given amplitude, zero offset and
    width.

    Parameters
    ----------
    x : array_like
        Input array variable
    A : float
        Amplitude
    x0 : float
        Zero offset
    w : float
        Width

    Returns
    -------
    array_like
        calculated array
    """
    return A*np.exp(- ((x - x0)/w)**2 /2.)

def supergauss(x, A, x0, w, o):
    """
    Calculate the Supergaussian functions with a given amplitude,
    zero offset, width and order.

    Parameters
    ----------
    x : array_like
        Input array variable
    A : float
        Amplitude
    x0 : float
        Zero offset
    w : float
        Width
    o : float
        order of the supergaussian

    Returns
    -------
    array_like
        calculated array
    """
    return A*np.exp(- ((x-x0)/w)**(2*o)/2.)

def sech(x, A, x0, w):
    """
    Calculate the hyperbolic secant function with a given
    amplitude, zero offset and width.

    Parameters
    ----------
    x : array_like
        Input array variable
    A : float
        Amplitude
    x0 : float
        Zero offset
    w : float
        Width

    Returns
    -------
    array_like
        calculated array
    """
    return A/np.cosh((x-x0)/w)

def factorial(n):
    """The factorial of n, i.e. n!"""
    if n == 0: return 1
    return n * factorial(n-1)

def linspacestep(start, step, N):
    """
    Create an array of given length for a given start and step
    value.

    Parameters
    ----------
    start : float
        first value to start with
    step : float
        size of the step
    N : int
        number of steps

    Returns
    -------
    out : array_like
        array of length N from start to start+N*step (not included)
    """
    return np.arange(start,start+N*step, step=step)

def lfsr_int(seed, mask):
    """
    A linear feedback shift register, using Galois or internal XOR
    implementation.

    Parameters
    ----------
    seed : int
        an integer representing the list of bits as the starting point of the
        register. Length N
    mask : int
        Determines the polynomial of the shift register (length N+1). The
        first and last bit of the mask must be 1.

    Yields
    ------
    xor : int
        output bit of the register
    state : int
        state of the register
    """
    state = seed
    nbits = mask.bit_length()-1
    while True:
        state = (state << 1)
        xor = state >> nbits
        #the modulus operation on has an effect if the last bit is 1
        if xor != 0:
            state ^= mask #this performs the modulus operation
        yield xor, state

def lfsr_ext(seed, taps, nbits):
    """A Fibonacci or external XOR linear feedback shift register.

    Parameters
    ----------
    seed : int
        binary number denoting the input state registers
    taps  : list
        list of registers that are input to the XOR (length 2)
    nbits : int
        number of registers

    Yields
    ------
    xor : int
        output bit of the registers
    state : int
        state of the register
    """
    sr = seed
    while 1:
        xor = 0
        for t in taps:
            if (sr & (1<<(nbits-t))) != 0:
                xor ^= 1
        sr = (xor << nbits-1) + (sr >> 1)
        yield xor, sr

def bool2bin(x):
    """
    Convert an array of boolean values into a binary number. If the input
    array is not a array of booleans it will be converted.
    """
    assert len(x)<64, "array must not be longer than 63"
    x = np.asarray(x, dtype=bool)
    y = 0
    for i, j in enumerate(x):
        y += j<<i
    return y

def find_offset(sequence, data):
    """
    Find index where binary sequence occurs fist in the binary data array

    Parameters
    ----------
    sequence : array_like
        sequence to search for inside the data
    data : array_like
        data array in which to find the sequence

    It is required that len(data) > sequence

    Returns
    -------
    idx : int
        index where sequence first occurs in data
    """
    assert len(data)>len(sequence), "data has to be longer than sequence"
    if not data.dtype==sequence.dtype:
        raise Warning("""data and sequence are not the same dtype, converting
        data to dtype of sequence""")
        data = data.astype(sequence.dtype)
    # using this string conversion method is much faster than array methods,
    # however it only finds the first occurence
    return data.tostring().index(sequence.tostring())//data.itemsize

def rolling_window(data, size):
    """
    Reshapes a 1D array into a 2D array with overlapping frames. Stops when the
    last value of data is reached.

    Parameters
    ----------
    data : array_like
        Data array to segment
    size : int
        The frame size

    Returns
    -------
    out : array_like
        output segmented 2D array


    Examples
    >>> mathfcts.rolling_window(np.arange(10), 3)
    array([[0, 1, 2],
            [1, 2, 3],
            [2, 3, 4],
            [3, 4, 5],
            [4, 5, 6],
            [5, 6, 7],
            [6, 7, 8],
            [7, 8, 9]])
    """
    shape = data.shape[:-1] + (data.shape[-1] - size + 1, size)
    strides = data.strides + (data. strides[-1],)
    return np.lib.stride_tricks.as_strided(data, shape=shape, strides=strides)

def resample(fold, fnew, signal, window=None):
    """
    Resamples a signal from an old frequency to a new. Preserves the whole data
    but adjusts the length of the array in the process.

    Parameters
    ----------
    fold : float
        Sampling frequency of the signal
    fnew : float
        New desired sampling frequency.
    window : array_like, optional
        sampling windowing function

    Returns
    -------
    out : array_like
        resampled signal of length fnew/fold*len(signal)

    """
    signal = signal.flatten()
    L = len(E)
    num = fnew/fold*L
    if window is None:
        signal = scisig.resample(signal, num)
    else:
        signal = scisig.resample(signal, num, window=window)
    return signal

def raisedcos(t, alpha, T=1):
    return np.sinc(t/T)*np.cos(t/T*pi*alpha)/(1-4*(alpha*t/T)**2)




