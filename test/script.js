class TodoList {
    constructor() {
        this.todos = JSON.parse(localStorage.getItem('todos')) || [];
        this.currentFilter = 'all';
        this.init();
    }

    init() {
        // Get DOM elements
        this.todoForm = document.getElementById('todo-form');
        this.todoInput = document.getElementById('todo-input');
        this.todoList = document.getElementById('todo-list');
        this.tasksCount = document.getElementById('tasks-count');
        this.clearCompletedBtn = document.getElementById('clear-completed');
        this.filterButtons = document.querySelectorAll('.filter-btn');

        // Add event listeners
        this.todoForm.addEventListener('submit', (e) => this.addTodo(e));
        this.clearCompletedBtn.addEventListener('click', () => this.clearCompleted());
        this.filterButtons.forEach(btn => {
            btn.addEventListener('click', () => this.changeFilter(btn.dataset.filter));
        });

        // Initial render
        this.render();
    }

    saveTodos() {
        localStorage.setItem('todos', JSON.stringify(this.todos));
    }

    addTodo(e) {
        e.preventDefault();
        const todoText = this.todoInput.value.trim();
        
        if (todoText) {
            const todo = {
                id: Date.now(),
                text: todoText,
                completed: false
            };
            
            this.todos.push(todo);
            this.saveTodos();
            this.todoInput.value = '';
            this.render();
        }
    }

    toggleTodo(id) {
        this.todos = this.todos.map(todo => {
            if (todo.id === id) {
                return { ...todo, completed: !todo.completed };
            }
            return todo;
        });
        this.saveTodos();
        this.render();
    }

    deleteTodo(id) {
        this.todos = this.todos.filter(todo => todo.id !== id);
        this.saveTodos();
        this.render();
    }

    clearCompleted() {
        this.todos = this.todos.filter(todo => !todo.completed);
        this.saveTodos();
        this.render();
    }

    changeFilter(filter) {
        this.currentFilter = filter;
        this.filterButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });
        this.render();
    }

    getFilteredTodos() {
        switch (this.currentFilter) {
            case 'active':
                return this.todos.filter(todo => !todo.completed);
            case 'completed':
                return this.todos.filter(todo => todo.completed);
            default:
                return this.todos;
        }
    }

    render() {
        const filteredTodos = this.getFilteredTodos();
        
        // Clear the current list
        this.todoList.innerHTML = '';
        
        // Render todos
        filteredTodos.forEach(todo => {
            const li = document.createElement('li');
            li.className = `todo-item ${todo.completed ? 'completed' : ''}`;
            
            li.innerHTML = `
                <input type="checkbox" class="todo-checkbox" ${todo.completed ? 'checked' : ''}>
                <span class="todo-text">${todo.text}</span>
                <button class="delete-btn">Delete</button>
            `;

            const checkbox = li.querySelector('.todo-checkbox');
            const deleteBtn = li.querySelector('.delete-btn');

            checkbox.addEventListener('change', () => this.toggleTodo(todo.id));
            deleteBtn.addEventListener('click', () => this.deleteTodo(todo.id));

            this.todoList.appendChild(li);
        });

        // Update tasks count
        const totalTasks = this.todos.length;
        const completedTasks = this.todos.filter(todo => todo.completed).length;
        this.tasksCount.textContent = `${totalTasks} tasks (${completedTasks} completed)`;
    }
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    new TodoList();
});