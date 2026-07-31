# Formula-First Examples

## Simple Harmonic Motion

**Answer**

Simple harmonic motion is sinusoidal because its differential equation has
purely imaginary characteristic roots.

**Setup**

For displacement \(x(t)\), mass \(m\), and spring constant \(k>0\),

\[
F=-kx,
\qquad
m\ddot{x}=F.
\]

Hence

\[
\ddot{x}+\omega^2x=0,
\qquad
\omega=\sqrt{\frac{k}{m}}.
\]

**Derivation**

Try \(x(t)=e^{rt}\):

\[
r^2+\omega^2=0
\quad\Longrightarrow\quad
r=\pm i\omega.
\]

Therefore

\[
x(t)=A\cos(\omega t)+B\sin(\omega t)
    =R\cos(\omega t-\phi).
\]

**Insight**

\[
\ddot{x}=-\omega^2x
\]

means acceleration always points toward equilibrium. Imaginary roots produce
rotation in phase space, hence periodic sine and cosine components.

**Verification**

\[
\frac{d^2}{dt^2}
\left[A\cos(\omega t)+B\sin(\omega t)\right]
=-\omega^2x(t).
\]

This satisfies the governing equation exactly.
