importScripts("https://www.gstatic.com/firebasejs/9.6.1/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging-compat.js");

firebase.initializeApp({
    apiKey: "AIzaSyCe2P2F6k9xvy2t71DtCGUxaoC3gxzeKHs",
    authDomain: "unipick-97be6.firebaseapp.com",
    projectId: "unipick-97be6",
    messagingSenderId: "885476484930",
    appId: "1:885476484930:web:fc8c99efeec6e78a85cadb"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
    console.log("🔥 BACKGROUND RECEIVED:", payload);

    const title =
        payload.notification?.title ||
        payload.data?.title ||
        "New Message";

    const options = {
        body:
            payload.notification?.body ||
            payload.data?.body ||
            "You have a new message",
        icon: "/static/logo.png",
    };

    self.registration.showNotification(title, options);
});


// 🔥 FORCE fallback (CRITICAL)
self.addEventListener("push", function(event) {

    let data = {};

    try {
        data = event.data.json();
    } catch (e) {}

    const title = data.title || "New Message";

    event.waitUntil(
        self.registration.showNotification(title, {
            body: data.body || "You have a new message",
            icon: "/static/logo.png",
        })
    );
});