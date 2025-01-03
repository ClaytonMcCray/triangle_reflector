from triangle import generate_triangle_reflections, analyze

if __name__ == "__main__":
    g = generate_triangle_reflections(50)
    print(g.display())
    print(analyze(g))
