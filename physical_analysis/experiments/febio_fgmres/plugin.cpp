#include <FECore/FECoreKernel.h>
#include <FECore/version.h>
#include "RestartFGMRESSolver.h"
FECORE_EXPORT unsigned int GetSDKVersion() { return FE_SDK_VERSION; }
FECORE_EXPORT void GetPluginVersion(int& major, int& minor, int& patch) { major=1; minor=0; patch=0; }
FECORE_EXPORT void PluginInitialize(FECoreKernel& febio) {
 FECoreKernel::SetInstance(&febio);
 REGISTER_FECORE_CLASS(RestartFGMRESSolver, "fgmres_restart_checked");
}
