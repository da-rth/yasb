// use wineventhook::{EventFilter, WindowEventHook};

// #[tokio::main]
// pub async fn event_listener() {
//     let (event_tx, mut event_rx) = tokio::sync::mpsc::unbounded_channel();

//     let hook = WindowEventHook::hook(
//         EventFilter::default(),
//         event_tx,
//     ).await.unwrap();

//     // Wait and print events
//     while let Some(event) = event_rx.recv().await {
//         println!("{:#?}", event);
//     }

//     hook.unhook().await.unwrap();
// }
