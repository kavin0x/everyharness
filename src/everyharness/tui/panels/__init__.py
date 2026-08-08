"""TUI panel widgets."""

from everyharness.tui.panels.doctor import DoctorPanel
from everyharness.tui.panels.library import LibraryPanel
from everyharness.tui.panels.model_detail import ModelDetailPanel
from everyharness.tui.panels.plugins import PluginsPanel
from everyharness.tui.panels.run_console import RunConsolePanel
from everyharness.tui.panels.serve import ServeStatusPanel
from everyharness.tui.panels.train import TrainWizardPanel
from everyharness.tui.panels.update import UpdatePanel

__all__ = [
    "DoctorPanel",
    "LibraryPanel",
    "ModelDetailPanel",
    "PluginsPanel",
    "RunConsolePanel",
    "ServeStatusPanel",
    "TrainWizardPanel",
    "UpdatePanel",
]
