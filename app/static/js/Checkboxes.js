function synchronize_checkboxes(col) {
let [ f1, ...r1 ] = document.querySelectorAll(`[class="${col}"]`);
let onChange = () => f1.checked = r1.every(n => n.checked);
f1.addEventListener('change', () => r1.forEach(n => n.checked = f1.checked));
r1.forEach(n => n.addEventListener('change', onChange));
}

for (let step = 1; step < 100; step++) {
    try {
        synchronize_checkboxes(step)
    } catch (error) {}
}