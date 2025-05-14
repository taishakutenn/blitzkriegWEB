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

window.addEventListener("beforeunload", function logData() {
    const bytes = new TextEncoder().encode(
            JSON.stringify(
                [[...document.querySelectorAll('.lvl_info')].map((x) => x = x.textContent)]
                .concat(
                [[...document.querySelectorAll('[type="checkbox"]')].map((x) => x = [x.name, x.checked])]
                )
                .concat(
                [[...document.querySelectorAll('[type="text"]')].map((x) => x = x.value)]
                )
            )
        );

    let data = new Blob([bytes],
    {'type': 'application/json;charset=utf-8'}
    );

    navigator.sendBeacon("/save_state", data);
});
