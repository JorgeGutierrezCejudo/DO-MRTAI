import gurobipy as gp
from gurobipy import GRB

# Nombre del archivo con el modelo
model_file = "model.lp"

try:
    # Cargar el modelo desde el archivo LP
    model = gp.read(model_file)

    # Optimizar el modelo
    model.optimize()

    # Verificar el estado de la solución
    if model.status == GRB.OPTIMAL:
        print("\n✅ Solución Óptima Encontrada")
        print(f"Valor Óptimo del Objetivo: {model.objVal:.4f}\n")

        # Mostrar los valores de las variables
        print("Valores de las Variables:")
        for v in model.getVars():
            print(f"{v.varName}: {v.x:.4f}")

    elif model.status == GRB.INFEASIBLE:
        print("\n❌ El modelo es INFACTIBLE. Intentando calcular IIS...")
        model.computeIIS()
        model.write("model.ilp")
        print("Se ha generado un archivo 'model.ilp' con el IIS para analizar la infactibilidad.")

    elif model.status == GRB.UNBOUNDED:
        print("\n⚠️ El modelo es NO ACOTADO.")

    else:
        print("\n⚠️ El modelo no se resolvió correctamente. Estado:", model.status)

except gp.GurobiError as e:
    print(f"Error de Gurobi: {e}")

except Exception as e:
    print(f"Error inesperado: {e}")
