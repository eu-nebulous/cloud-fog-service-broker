// utils/event-bus.js
export const EventBus = {
    events: {},
    dispatch(event, data) {
        if (!this.events[event]) return; // No subscribers
        this.events[event].forEach(callback => callback(data));
    },
    subscribe(event, callback) {
        if (!this.events[event]) this.events[event] = []; // New event
        this.events[event].push(callback);
    }
};
