import numpy as np
from scipy.integrate import odeint
from hashlib import shake_256
from PIL import Image

#5000 samples from 0 to 49.99 seconds
times = np.arange(5000)*0.01


def derivatives(state,time,m1,m2,l1,l2):
    theta1, theta2, omega1, omega2 = state
    g = 9.81
    delta = theta1 - theta2
    coupling = m2*l1*l2

    coefficients = [
        [(m1 + m2)*l1**2, coupling*np.cos(delta)],
        [coupling*np.cos(delta),m2*l2**2],
    ]

    right_side = [
        -(m1+m2)*g*l1*np.sin(theta1)
        - coupling * omega2**2 * np.sin(delta),
        -m2*g*l2*np.sin(theta2)
        + coupling * omega1**2 * np.sin(delta),
    ]

    alpha1,alpha2 = np.linalg.solve(coefficients,right_side)
    return[omega1,omega2,alpha1,alpha2]

def make_mask(theta1_deg, theta2_deg, m1, m2, l1, l2, byte_count):
    theta1, theta2 = np.deg2rad([theta1_deg, theta2_deg])
    initial_state = np.array([theta1, theta2, 0.0, 0.0])

    trajectory = odeint(
        derivatives,
        initial_state,
        times,
        args=(m1, m2, l1, l2),
        rtol=1e-9,
        atol=1e-9,
    )

    angles = trajectory[500:, :2]
    angle_sums = angles[:, 0] + angles[:, 1]
    scaled = np.trunc(angle_sums * 1_000_000_000)
    pendulum_bytes = (scaled % 256).astype(np.uint8)

    return shake_256(pendulum_bytes.tobytes()).digest(byte_count)

if __name__ == "__main__":

    with Image.open("sample.jpg") as image:
        #small_image = image.convert("RGB").resize((128, 128))
        pixels = np.array(image.convert("RGB"), dtype=np.uint8)

    print("Image shape:", pixels.shape)
    print("Number of color values:", pixels.size)
    print("First pixel RGB:", pixels[0, 0])

    mask = make_mask(120.0, -100.0, 1.0, 1.0, 1.0, 1.0, byte_count=pixels.size)

    print("Mask length:", len(mask))

    mask_array = np.frombuffer(mask, dtype=np.uint8).reshape(pixels.shape)

    encrypted_pixels = np.bitwise_xor(pixels, mask_array)

    Image.fromarray(encrypted_pixels).save("encrypted.png")

    print("First encrypted pixel:", encrypted_pixels[0, 0])
    print("Saved encrypted.png")

    with Image.open("encrypted.png") as image:
        saved_pixels = np.array(image, dtype=np.uint8)

    decrypted_pixels = np.bitwise_xor(saved_pixels, mask_array)

    Image.fromarray(decrypted_pixels).save("decrypted.png")

    print("First decrypted pixel:", decrypted_pixels[0, 0])
    print("Exact match:", np.array_equal(pixels, decrypted_pixels))


    guessed_mask = make_mask(
        120.0001, -100.0, 1.0, 1.0, 1.0, 1.0, byte_count=pixels.size
    )
    guessed_mask_array = np.frombuffer(guessed_mask, dtype=np.uint8).reshape(pixels.shape)

    wrong_pixels = np.bitwise_xor(saved_pixels, guessed_mask_array)
    Image.fromarray(wrong_pixels).save("wrong_key.png")

    print("Wrong key exact match:", np.array_equal(pixels, wrong_pixels))