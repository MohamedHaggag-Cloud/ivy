"""Collection of Jax random functions, wrapped to fit Ivy syntax and signature."""

# global
import jax as _jax
import jax.numpy as _jnp
from typing import Optional, Union, Tuple

# local
import ivy
from ivy.functional.backends.jax.device import to_dev
from ivy.functional.ivy.device import default_device
from ivy.functional.backends.jax import JaxArray


# Extra #
# ------#

RNG = _jax.random.PRNGKey(0)


def random_uniform(
    low: float = 0.0,
    high: float = 1.0,
    shape: Optional[Union[int, Tuple[int, ...]]] = None,
    device: Optional[ivy.Device] = None,
) -> JaxArray:
    global RNG
    RNG, rng_input = _jax.random.split(RNG)
    return to_dev(
        _jax.random.uniform(rng_input, shape if shape else (), minval=low, maxval=high),
        default_device(device),
    )


def random_normal(
    mean: float = 0.0,
    std: float = 1.0,
    shape: Optional[Union[int, Tuple[int, ...]]] = None,
    device: Optional[ivy.Device] = None,
) -> JaxArray:
    global RNG
    RNG, rng_input = _jax.random.split(RNG)
    return (
        to_dev(
            _jax.random.normal(rng_input, shape if shape else ()),
            default_device(device),
        )
        * std
        + mean
    )


def multinomial(
    population_size, num_samples, batch_size, probs=None, replace=True, device=None
):
    global RNG
    RNG, rng_input = _jax.random.split(RNG)
    if probs is None:
        probs = (
            _jnp.ones(
                (
                    batch_size,
                    population_size,
                )
            )
            / population_size
        )
    orig_probs_shape = list(probs.shape)
    num_classes = orig_probs_shape[-1]
    probs_flat = _jnp.reshape(probs, (-1, orig_probs_shape[-1]))
    probs_flat = probs_flat / _jnp.sum(probs_flat, -1, keepdims=True)
    probs_stack = _jnp.split(probs_flat, probs_flat.shape[0])
    samples_stack = [
        _jax.random.choice(rng_input, num_classes, (num_samples,), replace, p=prob[0])
        for prob in probs_stack
    ]
    samples_flat = _jnp.stack(samples_stack)
    return to_dev(
        _jnp.reshape(samples_flat, orig_probs_shape[:-1] + [num_samples]),
        default_device(device),
    )


def randint(low, high, shape, device=None):
    global RNG
    RNG, rng_input = _jax.random.split(RNG)
    return to_dev(
        _jax.random.randint(rng_input, shape, low, high), default_device(device)
    )


def seed(seed_value=0):
    global RNG
    RNG = _jax.random.PRNGKey(seed_value)
    return


def shuffle(x: JaxArray) -> JaxArray:
    global RNG
    RNG, rng_input = _jax.random.split(RNG)
    return _jax.random.shuffle(rng_input, x)