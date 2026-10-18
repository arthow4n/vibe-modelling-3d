#pragma once
// LP64 oneMKL RCI ABI. Declarations only; implementation stays in native libnumcore.
using MKL_INT = int;
extern "C" {
void dfgmres_init(const MKL_INT*, double*, double*, MKL_INT*, MKL_INT*, double*, double*);
void dfgmres_check(const MKL_INT*, const double*, const double*, MKL_INT*, MKL_INT*, double*, double*);
void dfgmres(const MKL_INT*, double*, double*, MKL_INT*, MKL_INT*, double*, double*);
void dfgmres_get(const MKL_INT*, double*, double*, MKL_INT*, const MKL_INT*, const double*, double*, MKL_INT*);
void MKL_Free_Buffers();
}
