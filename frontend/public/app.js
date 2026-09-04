const form = document.querySelector("#lead-form");
const status = document.querySelector("#form-status");
const submit = form.querySelector("button[type=submit]");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  status.className = "form-status";
  submit.disabled = true;
  submit.querySelector("span").textContent = "Submitting…";
  const data = Object.fromEntries(new FormData(form));
  data.source = "Website consultation form";
  delete data.whatsapp_consent;
  try {
    const response = await fetch("/api/intake", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Submission failed");
    form.reset();
    status.textContent = "Thank you — your inquiry has been received. Our team will contact you shortly.";
    status.classList.add("success");
  } catch {
    status.textContent = "We could not submit the form. Please call our office directly.";
    status.classList.add("error");
  } finally {
    submit.disabled = false;
    submit.querySelector("span").textContent = "Submit confidential inquiry";
  }
});
