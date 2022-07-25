use windows::Win32::UI::HiDpi::SetProcessDpiAwarenessContext;
use windows::Win32::UI::HiDpi::DPI_AWARENESS_CONTEXT_SYSTEM_AWARE;
use windows::core::Result as WindowsCrateResult;
use anyhow::Result;

trait ProcessWindowsCrateResult<T> {
  fn process(self) -> Result<T>;
}

impl<T> ProcessWindowsCrateResult<T> for WindowsCrateResult<T> {
  fn process(self) -> Result<T> {
    match self {
      Ok(value) => Ok(value),
      Err(error) => Err(error.into()),
    }
  }
}

pub fn setup_dpi_awareness_context() -> Result<()> {
  unsafe { SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_SYSTEM_AWARE) }.ok().process()
}