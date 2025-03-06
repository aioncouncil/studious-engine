from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import PhysicsSimulation, PhysicsInteraction

@login_required
def simulation_list(request):
    """Display a list of available physics simulations."""
    simulations = PhysicsSimulation.objects.all()
    return render(request, 'physics/simulation_list.html', {
        'simulations': simulations
    })

@login_required
def simulation_detail(request, simulation_id):
    """Display a specific physics simulation."""
    simulation = get_object_or_404(PhysicsSimulation, id=simulation_id)
    
    # Create or get an interaction record
    interaction, created = PhysicsInteraction.objects.get_or_create(
        simulation=simulation,
        user=request.user.profile,
        ended_at=None
    )
    
    return render(request, 'physics/simulation_detail.html', {
        'simulation': simulation,
        'interaction': interaction
    })

@login_required
def end_interaction(request, interaction_id):
    """End a physics interaction session."""
    interaction = get_object_or_404(PhysicsInteraction, id=interaction_id, user=request.user.profile)
    interaction.end_session()
    return redirect('physics:simulation_list')

@login_required
def simulation_api(request, simulation_id):
    """API endpoint for interacting with a physics simulation."""
    simulation = get_object_or_404(PhysicsSimulation, id=simulation_id)
    
    if request.method == 'GET':
        # Return simulation data
        return JsonResponse({
            'id': str(simulation.id),
            'name': simulation.name,
            'type': simulation.type,
            'entities': simulation.entities,
            'forces': simulation.forces,
            'constraints': simulation.constraints,
            'iteration_rate': simulation.iteration_rate,
            'visual_effects': simulation.visual_effects
        })
    
    elif request.method == 'POST':
        # Update interaction data
        interaction_id = request.POST.get('interaction_id')
        interaction_data = request.POST.get('interaction_data', '{}')
        
        interaction = get_object_or_404(PhysicsInteraction, id=interaction_id, user=request.user.profile)
        interaction.interaction_data = interaction_data
        interaction.save()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def simulation_create(request):
    """Create a new physics simulation."""
    if request.method == 'POST':
        # Basic simulation creation logic
        name = request.POST.get('name')
        sim_type = request.POST.get('type')
        iteration_rate = float(request.POST.get('iteration_rate', 60.0))
        
        # Create the simulation
        simulation = PhysicsSimulation.objects.create(
            name=name,
            type=sim_type,
            iteration_rate=iteration_rate,
            entities={},
            forces={},
            constraints={},
            visual_effects={}
        )
        
        return redirect('physics:simulation_detail', simulation_id=simulation.id)
    
    # GET request - show the creation form
    return render(request, 'physics/simulation_form.html', {
        'simulation_types': PhysicsSimulation.SIMULATION_TYPE_CHOICES
    })
