/* Это не анимация. Это дыхание. */
.core-sphere {
    animation: corePulse 2s ease-in-out infinite;
}

@keyframes corePulse {
    0% { transform: translate(-50%, -50%) scale(1); opacity: 0.6; }
    50% { transform: translate(-50%, -50%) scale(1.08); opacity: 0.9; }
    100% { transform: translate(-50%, -50%) scale(1); opacity: 0.6; }
}
