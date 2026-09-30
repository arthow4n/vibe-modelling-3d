"""Finite-strain recovery at FEBio's explicitly selected tet10 G8 points.

Native element-log principal strains are means. Recover extrema from nodal
kinematics, and require agreement of recovered means with those native fields.
This is not a printed-material constitutive or failure model.
"""
import numpy as np

# FEBio 4.13 FETet10G8 quadrature, FECore/FEElementTraits.cpp.
POINTS=np.array(((.0158359099,.3280546970,.3280546970),
                 (.3280546970,.0158359099,.3280546970),
                 (.3280546970,.3280546970,.0158359099),
                 (.3280546970,.3280546970,.3280546970),
                 (.6791431780,.1069522740,.1069522740),
                 (.1069522740,.6791431780,.1069522740),
                 (.1069522740,.1069522740,.6791431780),
                 (.1069522740,.1069522740,.1069522740)))


def derivatives(points):
    bary=np.column_stack((1-points.sum(axis=1),points))
    gradients=np.array(((-1,-1,-1),(1,0,0),(0,1,0),(0,0,1)))
    values=[(4*bary[:,i,None]-1)*gradients[i] for i in range(4)]
    for i,j in ((0,1),(1,2),(2,0),(0,3),(1,3),(2,3)):
        values.append(4*(bary[:,i,None]*gradients[j]+bary[:,j,None]*gradients[i]))
    return np.stack(values,axis=1)


class Tet10GreenStrain:
    def __init__(self,nodes,elements):
        self.elements=list(elements)
        self.connectivity=np.array([elements[e] for e in self.elements])
        self.reference=np.array([[nodes[n] for n in con] for con in self.connectivity])
        self.derivatives=derivatives(POINTS)
        jac=np.einsum('ena,qnb->eqab',self.reference,self.derivatives)
        if not np.isfinite(jac).all() or np.any(np.linalg.det(jac)<=0):
            raise ValueError('Nonpositive reference tet10 Jacobian at a strain point')
        self.inverse=np.linalg.inv(jac)

    def principal(self,displacements):
        current=self.reference+np.array([[displacements[n] for n in con] for con in self.connectivity])
        jac=np.einsum('ena,qnb->eqab',current,self.derivatives)
        if not np.isfinite(jac).all() or np.any(np.linalg.det(jac)<=0):
            raise ValueError('Nonpositive deformed tet10 Jacobian at a strain point')
        deformation=jac@self.inverse
        green=(np.swapaxes(deformation,-1,-2)@deformation-np.eye(3))/2
        return np.linalg.eigvalsh(green)
